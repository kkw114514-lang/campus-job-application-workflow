import Foundation
import Vision
import AppKit

// 用法: swift ocr.swift <图片路径> [候选正则]
let args = CommandLine.arguments
guard args.count >= 2 else { print("ERR: no image path"); exit(1) }
let path = args[1]
let pattern = args.count >= 3 ? args[2] : "^[A-Za-z0-9]{3,6}$"

guard let img = NSImage(contentsOfFile: path), let cg = img.cgImage(forProposedRect: nil, context: nil, hints: nil) else {
    print("ERR: cannot load image"); exit(1)
}
let req = VNRecognizeTextRequest()
req.recognitionLevel = .accurate
req.usesLanguageCorrection = false
req.recognitionLanguages = ["en-US"]
let handler = VNImageRequestHandler(cgImage: cg)
do { try handler.perform([req]) }
catch { fputs("ERR: OCR failed\n", stderr); exit(1) }
var cands: [String] = []
for obs in req.results ?? [] {
    if let t = obs.topCandidates(1).first {
        let s = t.string.trimmingCharacters(in: .whitespaces)
        if s.range(of: pattern, options: .regularExpression) != nil { cands.append(s) }

    }
}
print(cands.first ?? "NO_MATCH")
