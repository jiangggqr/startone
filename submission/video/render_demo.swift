import AppKit
import AVFoundation
import CoreGraphics
import CoreMedia
import CoreText
import CoreVideo
import Foundation
import ImageIO

struct Segment {
    let id: String
    let title: String
    let caption: String
    let captureURLs: [URL]
    let audioURL: URL
    let narration: String
    let audioDuration: CMTime
    let sceneDuration: CMTime
}

enum DemoError: Error, CustomStringConvertible {
    case message(String)

    var description: String {
        switch self {
        case .message(let value): return value
        }
    }
}

let canvasWidth = 1920
let canvasHeight = 1080
let framesPerSecond: Int32 = 24
let sceneGapSeconds = 0.72

func cgColor(_ red: CGFloat, _ green: CGFloat, _ blue: CGFloat, _ alpha: CGFloat = 1) -> CGColor {
    CGColor(red: red / 255, green: green / 255, blue: blue / 255, alpha: alpha)
}

let ink = cgColor(20, 35, 70)
let muted = cgColor(83, 95, 124)
let brand = cgColor(50, 84, 215)
let teal = cgColor(24, 126, 117)
let canvas = cgColor(246, 248, 252)
let line = cgColor(214, 221, 236)

func makeFont(size: CGFloat, bold: Bool) -> CTFont {
    let preferred = bold ? "SF Pro Display Semibold" : "SF Pro Display"
    return CTFontCreateWithName(preferred as CFString, size, nil)
}

func drawText(
    _ text: String,
    in rect: CGRect,
    context: CGContext,
    size: CGFloat,
    color: CGColor,
    bold: Bool = false,
    alignment: CTTextAlignment = .left
) {
    var paragraphAlignment = alignment
    let paragraph = withUnsafeBytes(of: &paragraphAlignment) { bytes -> CTParagraphStyle in
        let setting = CTParagraphStyleSetting(
            spec: .alignment,
            valueSize: bytes.count,
            value: bytes.baseAddress!
        )
        return CTParagraphStyleCreate([setting], 1)
    }
    let attributes: [NSAttributedString.Key: Any] = [
        NSAttributedString.Key(kCTFontAttributeName as String): makeFont(size: size, bold: bold),
        NSAttributedString.Key(kCTForegroundColorAttributeName as String): color,
        NSAttributedString.Key(kCTParagraphStyleAttributeName as String): paragraph,
    ]
    let attributed = NSAttributedString(string: text, attributes: attributes)
    let framesetter = CTFramesetterCreateWithAttributedString(attributed)
    let path = CGPath(rect: rect, transform: nil)
    let frame = CTFramesetterCreateFrame(framesetter, CFRangeMake(0, attributed.length), path, nil)
    CTFrameDraw(frame, context)
}

func loadImage(_ url: URL) -> CGImage? {
    guard FileManager.default.fileExists(atPath: url.path),
          let source = CGImageSourceCreateWithURL(url as CFURL, nil) else { return nil }
    return CGImageSourceCreateImageAtIndex(source, 0, nil)
}

func aspectFit(source: CGSize, inside target: CGRect) -> CGRect {
    let scale = min(target.width / source.width, target.height / source.height)
    let width = source.width * scale
    let height = source.height * scale
    return CGRect(
        x: target.midX - width / 2,
        y: target.midY - height / 2,
        width: width,
        height: height
    )
}

func activeSubtitle(for segment: Segment, progress: Double) -> String {
    let sentences = sentenceParts(segment.narration)
    guard !sentences.isEmpty else { return segment.caption }

    let wordCounts = sentences.map { max($0.split(whereSeparator: { $0.isWhitespace }).count, 1) }
    let totalWords = max(wordCounts.reduce(0, +), 1)
    let audioSeconds = CMTimeGetSeconds(segment.audioDuration)
    let sceneSeconds = CMTimeGetSeconds(segment.sceneDuration)
    let elapsed = min(max(progress, 0) * sceneSeconds, max(audioSeconds - 0.001, 0))

    var cursor = 0.0
    for (index, sentence) in sentences.enumerated() {
        let duration = audioSeconds * Double(wordCounts[index]) / Double(totalWords)
        if elapsed < cursor + duration { return sentence }
        cursor += duration
    }
    return sentences.last ?? segment.caption
}

func renderFrame(
    pixelBuffer: CVPixelBuffer,
    segment: Segment,
    progress: Double,
    segmentIndex: Int,
    segmentCount: Int
) throws {
    CVPixelBufferLockBaseAddress(pixelBuffer, [])
    defer { CVPixelBufferUnlockBaseAddress(pixelBuffer, []) }

    guard let baseAddress = CVPixelBufferGetBaseAddress(pixelBuffer),
          let context = CGContext(
            data: baseAddress,
            width: canvasWidth,
            height: canvasHeight,
            bitsPerComponent: 8,
            bytesPerRow: CVPixelBufferGetBytesPerRow(pixelBuffer),
            space: CGColorSpaceCreateDeviceRGB(),
            bitmapInfo: CGImageAlphaInfo.premultipliedFirst.rawValue | CGBitmapInfo.byteOrder32Little.rawValue
          ) else {
        throw DemoError.message("Could not create a video drawing context")
    }

    context.setFillColor(canvas)
    context.fill(CGRect(x: 0, y: 0, width: canvasWidth, height: canvasHeight))

    context.setFillColor(.white)
    context.fill(CGRect(x: 0, y: 980, width: canvasWidth, height: 100))
    context.setStrokeColor(line)
    context.setLineWidth(2)
    context.move(to: CGPoint(x: 0, y: 980))
    context.addLine(to: CGPoint(x: canvasWidth, y: 980))
    context.strokePath()

    drawText("StartOne", in: CGRect(x: 72, y: 1000, width: 300, height: 48), context: context, size: 34, color: ink, bold: true)
    drawText(segment.title, in: CGRect(x: 420, y: 1000, width: 1080, height: 48), context: context, size: 30, color: teal, bold: true, alignment: .center)
    drawText("\(segmentIndex + 1) / \(segmentCount)", in: CGRect(x: 1610, y: 1002, width: 230, height: 46), context: context, size: 26, color: muted, bold: true, alignment: .right)

    let screenshotBox = CGRect(x: 70, y: 205, width: 1780, height: 735)
    let rounded = CGPath(roundedRect: screenshotBox, cornerWidth: 24, cornerHeight: 24, transform: nil)
    context.saveGState()
    context.addPath(rounded)
    context.clip()
    context.setFillColor(.white)
    context.fill(screenshotBox)

    let availableCaptures = segment.captureURLs.compactMap { url -> (URL, CGImage)? in
        guard let image = loadImage(url) else { return nil }
        return (url, image)
    }

    if !availableCaptures.isEmpty {
        let imageIndex = min(Int(progress * Double(availableCaptures.count)), availableCaptures.count - 1)
        let image = availableCaptures[imageIndex].1
        var fit = aspectFit(source: CGSize(width: image.width, height: image.height), inside: screenshotBox.insetBy(dx: 8, dy: 8))
        let zoom = 1.0 + 0.016 * progress
        fit = CGRect(
            x: screenshotBox.midX - fit.width * zoom / 2,
            y: screenshotBox.midY - fit.height * zoom / 2,
            width: fit.width * zoom,
            height: fit.height * zoom
        )
        context.draw(image, in: fit)
    } else {
        context.setFillColor(cgColor(238, 242, 252))
        context.fill(screenshotBox)
        drawText("STARTONE", in: CGRect(x: 220, y: 685, width: 1480, height: 70), context: context, size: 34, color: teal, bold: true, alignment: .center)
        drawText(segment.title, in: CGRect(x: 210, y: 520, width: 1500, height: 150), context: context, size: 68, color: ink, bold: true, alignment: .center)
        drawText(segment.caption, in: CGRect(x: 300, y: 365, width: 1320, height: 120), context: context, size: 34, color: muted, alignment: .center)
    }
    context.restoreGState()

    context.addPath(rounded)
    context.setStrokeColor(line)
    context.setLineWidth(3)
    context.strokePath()

    context.setFillColor(.white)
    let captionCard = CGRect(x: 70, y: 28, width: 1780, height: 149)
    context.addPath(CGPath(roundedRect: captionCard, cornerWidth: 20, cornerHeight: 20, transform: nil))
    context.fillPath()
    context.setFillColor(brand)
    context.fill(CGRect(x: 70, y: 28, width: 12, height: 149))
    drawText(
        activeSubtitle(for: segment, progress: progress),
        in: CGRect(x: 120, y: 55, width: 1660, height: 96),
        context: context,
        size: 31,
        color: ink,
        bold: true,
        alignment: .center
    )
}

func parseTimeline(repoURL: URL) throws -> [Segment] {
    let videoURL = repoURL.appendingPathComponent("submission/video")
    let timelineURL = videoURL.appendingPathComponent("timeline.tsv")
    let content = try String(contentsOf: timelineURL, encoding: .utf8)
    var result: [Segment] = []

    for lineValue in content.split(separator: "\n", omittingEmptySubsequences: true) {
        let line = String(lineValue)
        if line.hasPrefix("#") { continue }
        let fields = line.components(separatedBy: "\t")
        guard fields.count == 4 else { throw DemoError.message("Invalid timeline row: \(line)") }
        let id = fields[0]
        let captureURLs = fields[3].split(separator: ",").map {
            videoURL.appendingPathComponent("captures").appendingPathComponent(String($0))
        }
        let naturalAudioURL = videoURL.appendingPathComponent("audio_natural/\(id).wav")
        let systemAudioURL = videoURL.appendingPathComponent("audio/\(id).aiff")
        let audioURL = FileManager.default.fileExists(atPath: naturalAudioURL.path)
            ? naturalAudioURL
            : systemAudioURL
        let narrationURL = videoURL.appendingPathComponent("segments/\(id).txt")
        let narration = try String(contentsOf: narrationURL, encoding: .utf8).trimmingCharacters(in: .whitespacesAndNewlines)
        let asset = AVURLAsset(url: audioURL)
        let duration = asset.duration
        guard CMTimeGetSeconds(duration).isFinite, CMTimeGetSeconds(duration) > 0 else {
            throw DemoError.message("Missing or invalid narration audio: \(audioURL.path)")
        }
        result.append(Segment(
            id: id,
            title: fields[1],
            caption: fields[2],
            captureURLs: captureURLs,
            audioURL: audioURL,
            narration: narration,
            audioDuration: duration,
            sceneDuration: CMTimeAdd(duration, CMTime(seconds: sceneGapSeconds, preferredTimescale: 600))
        ))
    }
    return result
}

func writeVisuals(segments: [Segment], to outputURL: URL) async throws {
    try? FileManager.default.removeItem(at: outputURL)
    let writer = try AVAssetWriter(outputURL: outputURL, fileType: .mp4)
    let outputSettings: [String: Any] = [
        AVVideoCodecKey: AVVideoCodecType.h264,
        AVVideoWidthKey: canvasWidth,
        AVVideoHeightKey: canvasHeight,
        AVVideoCompressionPropertiesKey: [
            AVVideoAverageBitRateKey: 5_200_000,
        ],
    ]
    let input = AVAssetWriterInput(mediaType: .video, outputSettings: outputSettings)
    input.expectsMediaDataInRealTime = false
    let adaptor = AVAssetWriterInputPixelBufferAdaptor(
        assetWriterInput: input,
        sourcePixelBufferAttributes: [
            kCVPixelBufferPixelFormatTypeKey as String: kCVPixelFormatType_32BGRA,
            kCVPixelBufferWidthKey as String: canvasWidth,
            kCVPixelBufferHeightKey as String: canvasHeight,
        ]
    )
    guard writer.canAdd(input) else { throw DemoError.message("Could not add video writer input") }
    writer.add(input)
    guard writer.startWriting() else { throw writer.error ?? DemoError.message("Could not start video writer") }
    writer.startSession(atSourceTime: .zero)

    var globalFrame: Int64 = 0
    for (segmentIndex, segment) in segments.enumerated() {
        let durationSeconds = CMTimeGetSeconds(segment.sceneDuration)
        let frameCount = max(Int(ceil(durationSeconds * Double(framesPerSecond))), 1)
        for localFrame in 0..<frameCount {
            while !input.isReadyForMoreMediaData {
                try await Task.sleep(nanoseconds: 2_000_000)
            }
            guard let pool = adaptor.pixelBufferPool else { throw DemoError.message("No pixel buffer pool") }
            var optionalBuffer: CVPixelBuffer?
            guard CVPixelBufferPoolCreatePixelBuffer(nil, pool, &optionalBuffer) == kCVReturnSuccess,
                  let buffer = optionalBuffer else { throw DemoError.message("Could not allocate video frame") }
            let progress = frameCount > 1 ? Double(localFrame) / Double(frameCount - 1) : 0
            try renderFrame(
                pixelBuffer: buffer,
                segment: segment,
                progress: progress,
                segmentIndex: segmentIndex,
                segmentCount: segments.count
            )
            let presentationTime = CMTime(value: globalFrame, timescale: framesPerSecond)
            guard adaptor.append(buffer, withPresentationTime: presentationTime) else {
                throw writer.error ?? DemoError.message("Could not append video frame")
            }
            globalFrame += 1
        }
        print("Rendered \(segment.id)")
    }

    input.markAsFinished()
    await withCheckedContinuation { continuation in
        writer.finishWriting { continuation.resume() }
    }
    guard writer.status == .completed else {
        throw writer.error ?? DemoError.message("Video writer did not complete")
    }
}

func sentenceParts(_ text: String) -> [String] {
    let pattern = #"(?<=[.!?])\s+"#
    guard let regex = try? NSRegularExpression(pattern: pattern) else { return [text] }
    let range = NSRange(text.startIndex..<text.endIndex, in: text)
    var parts: [String] = []
    var start = text.startIndex
    for match in regex.matches(in: text, range: range) {
        guard let splitRange = Range(match.range, in: text) else { continue }
        let part = text[start..<splitRange.lowerBound].trimmingCharacters(in: .whitespacesAndNewlines)
        if !part.isEmpty { parts.append(part) }
        start = splitRange.upperBound
    }
    let tail = text[start...].trimmingCharacters(in: .whitespacesAndNewlines)
    if !tail.isEmpty { parts.append(tail) }
    return parts.isEmpty ? [text] : parts
}

func srtTime(_ seconds: Double) -> String {
    let milliseconds = Int((seconds * 1000).rounded())
    let hours = milliseconds / 3_600_000
    let minutes = (milliseconds % 3_600_000) / 60_000
    let secs = (milliseconds % 60_000) / 1000
    let millis = milliseconds % 1000
    return String(format: "%02d:%02d:%02d,%03d", hours, minutes, secs, millis)
}

func writeSRT(segments: [Segment], to outputURL: URL) throws {
    var index = 1
    var cursor = 0.0
    var output = ""
    for segment in segments {
        let duration = CMTimeGetSeconds(segment.audioDuration)
        let sentences = sentenceParts(segment.narration)
        let wordCounts = sentences.map { max($0.split(whereSeparator: { $0.isWhitespace }).count, 1) }
        let totalWords = max(wordCounts.reduce(0, +), 1)
        var sentenceCursor = cursor
        for (sentenceIndex, sentence) in sentences.enumerated() {
            let share = Double(wordCounts[sentenceIndex]) / Double(totalWords)
            let sentenceDuration = duration * share
            output += "\(index)\n"
            output += "\(srtTime(sentenceCursor)) --> \(srtTime(sentenceCursor + sentenceDuration))\n"
            output += "\(sentence)\n\n"
            sentenceCursor += sentenceDuration
            index += 1
        }
        cursor += CMTimeGetSeconds(segment.sceneDuration)
    }
    try output.write(to: outputURL, atomically: true, encoding: .utf8)
}

func combineAudioAndVideo(segments: [Segment], visualsURL: URL, outputURL: URL) async throws {
    try? FileManager.default.removeItem(at: outputURL)
    let composition = AVMutableComposition()
    guard let compositionVideo = composition.addMutableTrack(withMediaType: .video, preferredTrackID: kCMPersistentTrackID_Invalid),
          let compositionAudio = composition.addMutableTrack(withMediaType: .audio, preferredTrackID: kCMPersistentTrackID_Invalid) else {
        throw DemoError.message("Could not create final composition tracks")
    }

    let visualsAsset = AVURLAsset(url: visualsURL)
    guard let sourceVideo = visualsAsset.tracks(withMediaType: .video).first else {
        throw DemoError.message("Rendered visuals contain no video track")
    }
    try compositionVideo.insertTimeRange(
        CMTimeRange(start: .zero, duration: visualsAsset.duration),
        of: sourceVideo,
        at: .zero
    )

    var cursor = CMTime.zero
    for segment in segments {
        let audioAsset = AVURLAsset(url: segment.audioURL)
        guard let sourceAudio = audioAsset.tracks(withMediaType: .audio).first else {
            throw DemoError.message("Narration contains no audio track: \(segment.audioURL.path)")
        }
        try compositionAudio.insertTimeRange(
            CMTimeRange(start: .zero, duration: segment.audioDuration),
            of: sourceAudio,
            at: cursor
        )
        cursor = CMTimeAdd(cursor, segment.sceneDuration)
    }

    guard let exporter = AVAssetExportSession(asset: composition, presetName: AVAssetExportPresetHighestQuality) else {
        throw DemoError.message("Could not create MP4 exporter")
    }
    exporter.outputURL = outputURL
    exporter.outputFileType = .mp4
    exporter.shouldOptimizeForNetworkUse = true
    await withCheckedContinuation { continuation in
        exporter.exportAsynchronously { continuation.resume() }
    }
    guard exporter.status == .completed else {
        throw exporter.error ?? DemoError.message("Final MP4 export did not complete")
    }
}

@main
struct StartOneDemoRenderer {
    static func main() async {
        do {
            guard CommandLine.arguments.count == 2 else {
                throw DemoError.message("Usage: render_demo.swift /absolute/path/to/repository")
            }
            let repoURL = URL(fileURLWithPath: CommandLine.arguments[1], isDirectory: true)
            let videoURL = repoURL.appendingPathComponent("submission/video")
            let buildURL = videoURL.appendingPathComponent("build")
            try FileManager.default.createDirectory(at: buildURL, withIntermediateDirectories: true)
            let segments = try parseTimeline(repoURL: repoURL)
            let visualsURL = buildURL.appendingPathComponent("StartOne_demo_visuals.mp4")
            let outputURL = videoURL.appendingPathComponent("StartOne_demo_final.mp4")
            let srtURL = videoURL.appendingPathComponent("StartOne_demo_en.srt")

            try writeSRT(segments: segments, to: srtURL)
            try await writeVisuals(segments: segments, to: visualsURL)
            try await combineAudioAndVideo(segments: segments, visualsURL: visualsURL, outputURL: outputURL)

            let seconds = segments.reduce(0.0) { $0 + CMTimeGetSeconds($1.sceneDuration) }
            print(String(format: "Created %@ (%.2f seconds)", outputURL.path, seconds))
            print("Created \(srtURL.path)")
        } catch {
            fputs("Video build failed: \(error)\n", stderr)
            exit(1)
        }
    }
}
