// swift-tools-version: 5.9
import PackageDescription

let package = Package(
    name: "OfficeDaysTracker",
    platforms: [
        .macOS(.v13)
    ],
    targets: [
        .target(
            name: "OfficeDaysTracker",
            path: "ControlOficina"
        )
    ]
)
