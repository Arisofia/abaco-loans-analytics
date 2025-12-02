# Zencoder VS Code Extension — ENOENT Fix (macOS, Windows, Linux)

Developers may encounter the following error when launching the Zencoder extension inside VS Code:

```
Failed to spawn Zencoder process: spawn /Users/<user>/.vscode/extensions/zencoderai.zencoder-3.7.9002-darwin-arm64/out/zencoder-cli ENOENT
```

This indicates that VS Code cannot locate the `zencoder-cli` binary shipped with the extension. Follow the steps below to restore a healthy installation.

> Paths differ by platform and VS Code edition:
>
> - **macOS**: `~/.vscode/extensions/zencoderai.zencoder-*` (Insiders: `~/.vscode-insiders/extensions`)
> - **Windows**: `%USERPROFILE%\.vscode\extensions\zencoderai.zencoder-*` (Insiders: `%USERPROFILE%\.vscode-insiders\extensions`)
> - **Linux**: `~/.vscode/extensions/zencoderai.zencoder-*` or the distribution-specific config directory (Insiders: `~/.vscode-insiders/extensions`)
> - **VS Code OSS / VSCodium**: use `.vscode-oss/extensions` in place of `.vscode` (e.g., `%USERPROFILE%\.vscode-oss\extensions` on Windows).
> - **Remote SSH / Dev Containers / Codespaces**: the extensions live inside the remote environment (e.g., `~/.vscode-server/extensions` or `~/.vscode-remote/extensions`); run the steps below from that context so the CLI path matches the runtime.

## Quick resolution checklist

1. **Uninstall the extension**: Open the Extensions view, locate **Zencoder**, select the gear icon, and choose **Uninstall**.
2. **Remove stale artifacts**: Ensure the old folder is deleted. Verify the platform-specific extension directory above (e.g., `%USERPROFILE%\\.vscode\\extensions`, `%USERPROFILE%\\.vscode-oss\\extensions`, or `~/.vscode/extensions`) no longer contains `zencoderai.zencoder-*`; repeat inside any remote workspace where you use the extension.
3. **Restart VS Code fully**: Quit the application (`⌘+Q`) to unload any background helpers.
4. **Reinstall Zencoder**: Install the extension again from the marketplace so VS Code downloads a clean `zencoder-cli` binary for your architecture.
5. **Verify permissions**: Confirm the CLI is executable (`chmod +x ~/.vscode/extensions/zencoderai.zencoder-*/out/zencoder-cli` on macOS/Linux). On Windows, ensure antivirus or group policies are not blocking the binary.
6. **Reopen the workspace**: Launch VS Code and reload the window to trigger a fresh spawn.

## Additional diagnostics

- If antivirus or endpoint protection tools are present, check their quarantine logs for `zencoder-cli` and whitelist the binary if necessary.
- For Apple Silicon vs. Intel Macs, make sure the downloaded extension architecture matches your machine; forcing a reinstall typically corrects mismatches.
- When working on remote containers, ensure the extension is installed in the *remote* VS Code server (Extensions view → Remote) so the binary path resolves inside the container.

Following this checklist addresses the ENOENT cause (missing binary) without changing repository code, keeping local development environments consistent for all contributors.
