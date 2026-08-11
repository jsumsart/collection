import CoreGraphics
import Foundation
import ImageIO
import UniformTypeIdentifiers

struct FeaturedSpec {
    let input: String
    let output: String
    let manualCrop: CGRect?
}

let specs: [FeaturedSpec] = [
    .init(
        input: "objects/catalog-thumbs/fig-072_thomas-eloby-landscape-n-d.png",
        output: "assets/featured/coll005.png",
        manualCrop: CGRect(x: 48, y: 42, width: 480, height: 624)
    ),
    .init(input: "objects/catalog-thumbs/fig-005_frederick-flemister-the-plotters-1940-oil-on-canvas.png", output: "assets/featured/coll046.png", manualCrop: nil),
    .init(input: "objects/catalog-thumbs/fig-086_lucky-sibiya-women-with-animals-1979.png", output: "assets/featured/coll016.png", manualCrop: nil),
    .init(input: "objects/catalog-thumbs/fig-095_edward-colker-sign-and-symbol-106-210-1967.png", output: "assets/featured/coll025.png", manualCrop: nil),
    .init(
        input: "objects/catalog-thumbs/fig-094_jeane-b-oosting.png",
        output: "assets/featured/coll038.png",
        manualCrop: CGRect(x: 0, y: 166, width: 576, height: 296)
    ),
    .init(input: "objects/catalog-thumbs/fig-004_hale-aspacio-woodruff-portrait-of-paul-johnson-sr-1943.png", output: "assets/featured/coll048.png", manualCrop: nil),
    .init(input: "objects/catalog-thumbs/fig-035_brockford-gordon-jackson-flood-1979.jpg.png", output: "assets/featured/coll055.png", manualCrop: nil),
    .init(input: "objects/catalog-thumbs/fig-097_kojin-toneyama-sunset-191-210-1966.png", output: "assets/featured/coll076.png", manualCrop: nil),
    .init(
        input: "objects/catalog-thumbs/fig-025_vase-by-marcus-douyon-1972.png",
        output: "assets/featured/coll083.png",
        manualCrop: CGRect(x: 34, y: 34, width: 508, height: 612)
    ),
]

let fileManager = FileManager.default
let cwd = URL(fileURLWithPath: fileManager.currentDirectoryPath)
let whiteThreshold = 242
let alphaThreshold = 20
let edgeInkThreshold = 6

func loadImage(at url: URL) -> CGImage? {
    guard let source = CGImageSourceCreateWithURL(url as CFURL, nil) else {
        return nil
    }
    return CGImageSourceCreateImageAtIndex(source, 0, nil)
}

func rgbaBytes(for image: CGImage) -> [UInt8]? {
    let width = image.width
    let height = image.height
    let bytesPerPixel = 4
    let bytesPerRow = bytesPerPixel * width
    var buffer = [UInt8](repeating: 0, count: height * bytesPerRow)

    guard let colorSpace = CGColorSpace(name: CGColorSpace.sRGB) else {
        return nil
    }

    let bitmapInfo = CGImageAlphaInfo.premultipliedLast.rawValue | CGBitmapInfo.byteOrder32Big.rawValue
    guard let context = CGContext(
        data: &buffer,
        width: width,
        height: height,
        bitsPerComponent: 8,
        bytesPerRow: bytesPerRow,
        space: colorSpace,
        bitmapInfo: bitmapInfo
    ) else {
        return nil
    }

    context.draw(image, in: CGRect(x: 0, y: 0, width: width, height: height))
    return buffer
}

func contentBounds(for image: CGImage) -> CGRect {
    guard let buffer = rgbaBytes(for: image) else {
        return CGRect(x: 0, y: 0, width: image.width, height: image.height)
    }

    let width = image.width
    let height = image.height
    let bytesPerPixel = 4
    var minX = width
    var minY = height
    var maxX = 0
    var maxY = 0
    var found = false

    for y in 0..<height {
        for x in 0..<width {
            let offset = ((y * width) + x) * bytesPerPixel
            let r = Int(buffer[offset])
            let g = Int(buffer[offset + 1])
            let b = Int(buffer[offset + 2])
            let a = Int(buffer[offset + 3])

            let isOpaque = a > alphaThreshold
            let isNearWhite = r > whiteThreshold && g > whiteThreshold && b > whiteThreshold

            if isOpaque && !isNearWhite {
                minX = min(minX, x)
                minY = min(minY, y)
                maxX = max(maxX, x)
                maxY = max(maxY, y)
                found = true
            }
        }
    }

    guard found else {
        return CGRect(x: 0, y: 0, width: width, height: height)
    }

    return CGRect(
        x: minX,
        y: minY,
        width: maxX - minX + 1,
        height: maxY - minY + 1
    )
}

func trimEdgeWhitespace(for image: CGImage, from bounds: CGRect) -> CGRect {
    guard let buffer = rgbaBytes(for: image) else {
        return bounds
    }

    let width = image.width
    let height = image.height
    let bytesPerPixel = 4

    func pixelIsInk(_ x: Int, _ y: Int) -> Bool {
        let offset = ((y * width) + x) * bytesPerPixel
        let r = Int(buffer[offset])
        let g = Int(buffer[offset + 1])
        let b = Int(buffer[offset + 2])
        let a = Int(buffer[offset + 3])

        let isOpaque = a > alphaThreshold
        let isNearWhite = r > whiteThreshold && g > whiteThreshold && b > whiteThreshold
        return isOpaque && !isNearWhite
    }

    var minX = max(0, Int(bounds.minX))
    var maxX = min(width - 1, Int(bounds.maxX))
    var minY = max(0, Int(bounds.minY))
    var maxY = min(height - 1, Int(bounds.maxY))

    func rowInkCount(_ y: Int) -> Int {
        var count = 0
        for x in minX...maxX where pixelIsInk(x, y) {
            count += 1
        }
        return count
    }

    func columnInkCount(_ x: Int) -> Int {
        var count = 0
        for y in minY...maxY where pixelIsInk(x, y) {
            count += 1
        }
        return count
    }

    while minY < maxY && rowInkCount(minY) <= edgeInkThreshold {
        minY += 1
    }
    while maxY > minY && rowInkCount(maxY) <= edgeInkThreshold {
        maxY -= 1
    }
    while minX < maxX && columnInkCount(minX) <= edgeInkThreshold {
        minX += 1
    }
    while maxX > minX && columnInkCount(maxX) <= edgeInkThreshold {
        maxX -= 1
    }

    return CGRect(x: minX, y: minY, width: maxX - minX + 1, height: maxY - minY + 1)
}

func fittedCropRect(for image: CGImage, contentRect: CGRect) -> CGRect {
    let imageRect = CGRect(x: 0, y: 0, width: image.width, height: image.height)
    let marginX = contentRect.width * 0.06
    let marginY = contentRect.height * 0.06
    let expanded = contentRect.insetBy(dx: -marginX, dy: -marginY).intersection(imageRect)

    let targetAspect = 4.0 / 3.0
    var cropWidth = max(expanded.width, expanded.height * targetAspect)
    var cropHeight = cropWidth / targetAspect

    if cropHeight > imageRect.height {
        cropHeight = imageRect.height
        cropWidth = cropHeight * targetAspect
    }

    if cropWidth > imageRect.width {
        cropWidth = imageRect.width
        cropHeight = cropWidth / targetAspect
    }

    var originX = expanded.midX - cropWidth / 2
    var originY = expanded.midY - cropHeight / 2

    originX = min(max(0, originX), imageRect.width - cropWidth)
    originY = min(max(0, originY), imageRect.height - cropHeight)

    let finalRect = CGRect(x: originX, y: originY, width: cropWidth, height: cropHeight)
    return finalRect.integral
}

func writePNG(image: CGImage, to url: URL) throws {
    guard let destination = CGImageDestinationCreateWithURL(url as CFURL, UTType.png.identifier as CFString, 1, nil) else {
        throw NSError(domain: "FeaturedCrops", code: 2, userInfo: [NSLocalizedDescriptionKey: "Could not create image destination"])
    }
    CGImageDestinationAddImage(destination, image, nil)
    guard CGImageDestinationFinalize(destination) else {
        throw NSError(domain: "FeaturedCrops", code: 3, userInfo: [NSLocalizedDescriptionKey: "Could not finalize PNG"])
    }
}

for spec in specs {
    let inputURL = cwd.appendingPathComponent(spec.input)
    let outputURL = cwd.appendingPathComponent(spec.output)
    try fileManager.createDirectory(at: outputURL.deletingLastPathComponent(), withIntermediateDirectories: true)

    guard let image = loadImage(at: inputURL) else {
        fputs("Could not load image at \(spec.input)\n", stderr)
        continue
    }

    let cropRect: CGRect
    if let manualCrop = spec.manualCrop {
        cropRect = manualCrop.integral
    } else {
        let bounds = trimEdgeWhitespace(for: image, from: contentBounds(for: image))
        cropRect = fittedCropRect(for: image, contentRect: bounds)
    }

    guard let result = image.cropping(to: cropRect) else {
        fputs("Could not crop featured image for \(spec.input)\n", stderr)
        continue
    }

    try writePNG(image: result, to: outputURL)
    print("Wrote \(spec.output)")
}
