import AppKit
import Foundation

let args = CommandLine.arguments

guard args.count >= 3 else {
    fputs("Usage: swift generate_catalog_thumbs.swift <input-dir> <output-dir>\n", stderr)
    exit(1)
}

let inputDir = URL(fileURLWithPath: args[1], isDirectory: true)
let outputDir = URL(fileURLWithPath: args[2], isDirectory: true)
let fileManager = FileManager.default

let maxDimension: CGFloat = 1280
let watermarkText = "JSU Department of Art Permanent Collection"

try? fileManager.createDirectory(at: outputDir, withIntermediateDirectories: true)

func outputRep(for image: NSImage) -> NSBitmapImageRep? {
    guard
        let tiffData = image.tiffRepresentation,
        let rep = NSBitmapImageRep(data: tiffData)
    else {
        return nil
    }

    return rep
}

func resizedSize(for size: CGSize) -> CGSize {
    let longest = max(size.width, size.height)
    guard longest > maxDimension else {
        return size
    }

    let scale = maxDimension / longest
    return CGSize(width: floor(size.width * scale), height: floor(size.height * scale))
}

func makeWatermarkedImage(from url: URL, destination: URL) throws {
    guard let image = NSImage(contentsOf: url) else {
        throw NSError(domain: "Thumbs", code: 1, userInfo: [NSLocalizedDescriptionKey: "Unable to open \(url.path)"])
    }

    let sourceSize = image.size
    let targetSize = resizedSize(for: sourceSize)
    let targetRect = CGRect(origin: .zero, size: targetSize)

    guard let bitmap = NSBitmapImageRep(
        bitmapDataPlanes: nil,
        pixelsWide: Int(targetSize.width),
        pixelsHigh: Int(targetSize.height),
        bitsPerSample: 8,
        samplesPerPixel: 4,
        hasAlpha: true,
        isPlanar: false,
        colorSpaceName: .deviceRGB,
        bytesPerRow: 0,
        bitsPerPixel: 0
    ) else {
        throw NSError(domain: "Thumbs", code: 2, userInfo: [NSLocalizedDescriptionKey: "Unable to allocate output bitmap"])
    }

    bitmap.size = targetSize
    NSGraphicsContext.saveGraphicsState()
    guard let context = NSGraphicsContext(bitmapImageRep: bitmap) else {
        NSGraphicsContext.restoreGraphicsState()
        throw NSError(domain: "Thumbs", code: 3, userInfo: [NSLocalizedDescriptionKey: "Unable to create graphics context"])
    }

    NSGraphicsContext.current = context
    context.imageInterpolation = .high

    NSColor.white.setFill()
    targetRect.fill()
    image.draw(in: targetRect, from: CGRect(origin: .zero, size: sourceSize), operation: .sourceOver, fraction: 1.0)

    let fontSize = max(20, min(targetSize.width, targetSize.height) * 0.06)
    let paragraph = NSMutableParagraphStyle()
    paragraph.alignment = .center

    let attributes: [NSAttributedString.Key: Any] = [
        .font: NSFont.systemFont(ofSize: fontSize, weight: .bold),
        .foregroundColor: NSColor(calibratedWhite: 1.0, alpha: 0.18),
        .paragraphStyle: paragraph
    ]

    let text = NSAttributedString(string: watermarkText, attributes: attributes)
    let textSize = text.size()

    let cgContext = context.cgContext
    cgContext.saveGState()
    cgContext.translateBy(x: targetSize.width / 2, y: targetSize.height / 2)
    cgContext.rotate(by: -.pi / 5.8)
    cgContext.translateBy(x: -targetSize.width / 2, y: -targetSize.height / 2)

    let stepX = max(textSize.width + 90, 280)
    let stepY = max(textSize.height + 80, 180)

    var y = -targetSize.height
    while y < targetSize.height * 2 {
        var x = -targetSize.width
        while x < targetSize.width * 2 {
            let rect = CGRect(x: x, y: y, width: textSize.width, height: textSize.height)
            text.draw(in: rect)
            x += stepX
        }
        y += stepY
    }

    cgContext.restoreGState()
    NSGraphicsContext.restoreGraphicsState()

    guard let data = bitmap.representation(using: .png, properties: [:]) else {
        throw NSError(domain: "Thumbs", code: 4, userInfo: [NSLocalizedDescriptionKey: "Unable to encode PNG for \(url.lastPathComponent)"])
    }

    try data.write(to: destination)
}

let validExtensions = Set(["png", "jpg", "jpeg", "tif", "tiff", "webp"])
let inputFiles = (try fileManager.contentsOfDirectory(at: inputDir, includingPropertiesForKeys: nil))
    .filter { validExtensions.contains($0.pathExtension.lowercased()) }
    .sorted { $0.lastPathComponent.localizedCaseInsensitiveCompare($1.lastPathComponent) == .orderedAscending }

for file in inputFiles {
    let destination = outputDir.appendingPathComponent(file.deletingPathExtension().lastPathComponent + ".png")
    do {
        try makeWatermarkedImage(from: file, destination: destination)
        print("thumb \(destination.lastPathComponent)")
    } catch {
        fputs("error \(file.lastPathComponent): \(error.localizedDescription)\n", stderr)
    }
}
