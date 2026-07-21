import AVFoundation
import Foundation
import ImageIO
import UniformTypeIdentifiers

guard CommandLine.arguments.count >= 4 else {
    fputs("Usage: extract_frames VIDEO OUTPUT_DIR SECOND...\n", stderr)
    exit(2)
}

let videoURL = URL(fileURLWithPath: CommandLine.arguments[1])
let outputURL = URL(fileURLWithPath: CommandLine.arguments[2], isDirectory: true)
try FileManager.default.createDirectory(at: outputURL, withIntermediateDirectories: true)

let asset = AVURLAsset(url: videoURL)
let generator = AVAssetImageGenerator(asset: asset)
generator.appliesPreferredTrackTransform = true
generator.requestedTimeToleranceBefore = .zero
generator.requestedTimeToleranceAfter = .zero

for value in CommandLine.arguments.dropFirst(3) {
    guard let second = Double(value) else { continue }
    let time = CMTime(seconds: second, preferredTimescale: 600)
    var actual = CMTime.zero
    let image = try generator.copyCGImage(at: time, actualTime: &actual)
    let name = String(format: "frame_%06.2f.png", second)
    let target = outputURL.appendingPathComponent(name)
    guard let destination = CGImageDestinationCreateWithURL(
        target as CFURL,
        UTType.png.identifier as CFString,
        1,
        nil
    ) else {
        throw NSError(domain: "StartOneVideo", code: 1)
    }
    CGImageDestinationAddImage(destination, image, nil)
    guard CGImageDestinationFinalize(destination) else {
        throw NSError(domain: "StartOneVideo", code: 2)
    }
    print(target.path)
}
