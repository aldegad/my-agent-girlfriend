// swift-tools-version: 5.9
import PackageDescription

let package = Package(
    name: "GirlfriendDesktop",
    platforms: [
        .macOS(.v13),
    ],
    products: [
        .executable(name: "GirlfriendDesktop", targets: ["GirlfriendDesktop"]),
    ],
    targets: [
        .executableTarget(
            name: "GirlfriendDesktop",
            path: "Sources/GirlfriendDesktop"
        ),
    ]
)
