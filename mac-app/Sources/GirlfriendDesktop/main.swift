import Foundation
import AppKit
import SwiftUI

private let bridgeBaseURL = URL(string: "http://127.0.0.1:44777")!
private let projectRoot = "/Users/soohongkim/Documents/workspace/personal/my-agent-girlfriend"

struct BridgeActivationResponse: Decodable {
    let onboarding_step: String
    let reply: String
    let image_path: String?
    let assistant_name: String?
    let user_name: String?
}

struct BridgeChatResponse: Decodable {
    let onboarding_step: String
    let reply: String
    let preset_id: String?
    let image_path: String?
    let assistant_name: String?
    let user_name: String?
}

struct ChatBubble: Identifiable {
    let id = UUID()
    let role: String
    let text: String
}

@MainActor
final class BridgeViewModel: ObservableObject {
    @Published var currentImage: NSImage?
    @Published var isBooting = true
    @Published var overlayLine: String = "안녕. 너는 뭐라고 불리고 싶어?"

    private var bridgeTask: Process?

    func boot() {
        Task {
            let alreadyReady = await bridgeIsReady()
            if !alreadyReady {
                launchBridge()
                try? await Task.sleep(for: .seconds(1.2))
            }
            await activate()
            await watchSession()
            isBooting = false
        }
    }

    private func launchBridge() {
        let task = Process()
        task.currentDirectoryURL = URL(fileURLWithPath: projectRoot)
        task.executableURL = URL(fileURLWithPath: "/usr/bin/env")
        task.arguments = ["uv", "run", "python", "scripts/run_bridge.py", "--host", "127.0.0.1", "--port", "44777"]
        try? task.run()
        bridgeTask = task
    }

    private func bridgeIsReady() async -> Bool {
        do {
            let (_, response) = try await URLSession.shared.data(from: bridgeBaseURL.appending(path: "/health"))
            if let http = response as? HTTPURLResponse {
                return http.statusCode == 200
            }
        } catch {
            return false
        }
        return false
    }

    private func activate() async {
        var request = URLRequest(url: bridgeBaseURL.appending(path: "/v1/activate"))
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        guard let response: BridgeActivationResponse = await load(request) else { return }
        overlayLine = response.reply
        loadImage(path: response.image_path)
    }

    private func watchSession() async {
        while true {
            try? await Task.sleep(for: .seconds(1.0))
            await refreshSession()
        }
    }

    private func refreshSession() async {
        var request = URLRequest(url: bridgeBaseURL.appending(path: "/v1/session"))
        request.httpMethod = "GET"
        guard let response: BridgeActivationResponse = await load(request, emitErrorMessage: false) else { return }
        overlayLine = response.reply
        loadImage(path: response.image_path)
    }

    private func loadImage(path: String?) {
        guard let path, !path.isEmpty else {
            currentImage = nil
            return
        }
        currentImage = NSImage(contentsOfFile: path)
    }

    private func load<T: Decodable>(_ request: URLRequest, emitErrorMessage: Bool = true) async -> T? {
        do {
            let (data, _) = try await URLSession.shared.data(for: request)
            return try JSONDecoder().decode(T.self, from: data)
        } catch {
            if emitErrorMessage {
                overlayLine = "브릿지를 다시 깨우는 중이야."
            }
            return nil
        }
    }
}

struct FloatingPanelView: View {
    @StateObject private var viewModel = BridgeViewModel()

    var body: some View {
        ZStack {
            LinearGradient(
                colors: [Color(red: 1.0, green: 0.96, blue: 0.95), Color(red: 1.0, green: 0.91, blue: 0.9)],
                startPoint: .topLeading,
                endPoint: .bottomTrailing
            )
            .ignoresSafeArea()

            VStack(spacing: 0) {
                Group {
                    if let image = viewModel.currentImage {
                        Image(nsImage: image)
                            .resizable()
                            .scaledToFit()
                            .frame(maxWidth: .infinity)
                            .frame(height: 720)
                            .clipShape(RoundedRectangle(cornerRadius: 24, style: .continuous))
                    } else {
                        RoundedRectangle(cornerRadius: 24, style: .continuous)
                            .fill(.white.opacity(0.72))
                            .overlay(
                                Text(viewModel.isBooting ? "브릿지 깨우는 중..." : viewModel.overlayLine)
                                    .font(.system(size: 18, weight: .semibold, design: .rounded))
                                    .foregroundStyle(.secondary)
                                    .padding(24)
                            )
                            .frame(height: 720)
                    }
                }
            }
            .padding(8)
        }
        .frame(width: 430, height: 740)
        .task {
            viewModel.boot()
        }
    }
}

@main
struct GirlfriendDesktopApp: App {
    var body: some Scene {
        WindowGroup {
            FloatingPanelView()
                .background(WindowAccessor())
        }
        .windowResizability(.contentSize)
    }
}

struct WindowAccessor: NSViewRepresentable {
    func makeNSView(context: Context) -> NSView {
        let view = NSView()
        DispatchQueue.main.async {
            NSApp.setActivationPolicy(.regular)
            NSApp.activate(ignoringOtherApps: true)
            if let window = view.window {
                window.level = .floating
                window.collectionBehavior = [.canJoinAllSpaces, .fullScreenAuxiliary]
                window.titleVisibility = .hidden
                window.titlebarAppearsTransparent = true
                window.isMovableByWindowBackground = true
                window.standardWindowButton(.zoomButton)?.isHidden = true
            }
        }
        return view
    }

    func updateNSView(_ nsView: NSView, context: Context) {}
}
