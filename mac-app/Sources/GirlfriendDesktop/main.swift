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
    let muted: Bool?
}

struct MuteResponse: Decodable {
    let muted: Bool
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
    @Published var muted: Bool = false

    private var bridgeTask: Process?

    func boot() {
        Task {
            let alreadyReady = await bridgeIsReady()
            if !alreadyReady {
                launchBridge()
                try? await Task.sleep(for: .seconds(1.2))
            }
            await activate()
            isBooting = false
            await watchSession()
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
        if let muted = response.muted { self.muted = muted }
    }

    func toggleMute() {
        let next = !muted
        muted = next
        Task {
            var request = URLRequest(url: bridgeBaseURL.appending(path: "/v1/mute"))
            request.httpMethod = "POST"
            request.setValue("application/json", forHTTPHeaderField: "Content-Type")
            request.httpBody = try? JSONSerialization.data(withJSONObject: ["muted": next])
            _ = await load(request) as MuteResponse?
        }
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
        ZStack(alignment: .topTrailing) {
            ZStack {
                if let image = viewModel.currentImage {
                    Image(nsImage: image)
                        .resizable()
                        .scaledToFill()
                        .frame(width: 480, height: 720)
                        .clipped()
                } else {
                    Color(red: 1.0, green: 0.94, blue: 0.93)
                    Text(viewModel.isBooting ? "브릿지 깨우는 중..." : viewModel.overlayLine)
                        .font(.system(size: 22, weight: .semibold, design: .rounded))
                        .foregroundStyle(Color(red: 0.28, green: 0.17, blue: 0.2))
                        .multilineTextAlignment(.center)
                        .padding(32)
                }
            }
            .frame(width: 480, height: 720)

            Button(action: { viewModel.toggleMute() }) {
                Image(systemName: viewModel.muted ? "speaker.slash.fill" : "speaker.wave.2.fill")
                    .font(.system(size: 16, weight: .semibold))
                    .foregroundStyle(viewModel.muted ? Color.white.opacity(0.92) : Color(red: 0.28, green: 0.17, blue: 0.2))
                    .frame(width: 36, height: 36)
                    .background(
                        Circle()
                            .fill(viewModel.muted ? Color(red: 0.92, green: 0.45, blue: 0.61).opacity(0.95) : Color.white.opacity(0.85))
                    )
                    .overlay(Circle().stroke(Color.black.opacity(0.10), lineWidth: 1))
                    .shadow(color: Color.black.opacity(0.18), radius: 4, x: 0, y: 2)
            }
            .buttonStyle(.plain)
            .padding(14)
            .help(viewModel.muted ? "음소거 해제" : "음소거")
        }
        .frame(width: 480, height: 720)
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
