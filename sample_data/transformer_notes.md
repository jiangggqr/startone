# Transformer learning notes

## 1. Why Transformer was introduced

Sequence models need to represent how each token relates to other tokens. Recurrent models process tokens step by step, which limits parallel processing and can make long-range relationships difficult to capture.

## 2. Self-attention

Self-attention lets each position compare itself with other positions in the same sequence. It first computes how relevant other positions are, then uses those relevance scores to combine information from the corresponding value representations.

### 2.1 Query, Key and Value

Each token representation is projected into a query, a key and a value. A query is compared with keys to produce attention scores. The scores are normalized and used as weights for a weighted sum of values.

### 2.2 Scaled dot-product attention

The dot product between a query and keys produces raw attention scores. Dividing by the square root of the key dimension helps keep the score scale stable before softmax.

## 3. Positional information

Self-attention alone does not encode token order. Positional information is added so the model can distinguish different positions in the sequence.

## 4. Multi-head attention

Multiple attention heads learn different projections and can capture different relationships. Their outputs are concatenated and projected again.
