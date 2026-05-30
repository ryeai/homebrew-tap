class Rye < Formula
  desc "AI agent proxy and audit CLI"
  homepage "https://rye.ai"
  version "0.7.2"
  license "Apache-2.0"

  on_macos do
    if Hardware::CPU.arm?
      url "https://storage.googleapis.com/barn.rye.ai/releases/0.7.2/homebrew/rye-0.7.2-darwin-arm64.tar.gz"
      sha256 "PUT_DARWIN_ARM64_SHA256_HERE"
    else
      url "https://storage.googleapis.com/barn.rye.ai/releases/0.7.2/homebrew/rye-0.7.2-darwin-x64.tar.gz"
      sha256 "PUT_DARWIN_X64_SHA256_HERE"
    end
  end

  on_linux do
    if Hardware::CPU.arm?
      url "https://storage.googleapis.com/barn.rye.ai/releases/0.7.2/homebrew/rye-0.7.2-linux-arm64-musl.tar.gz"
      sha256 "PUT_LINUX_ARM64_SHA256_HERE"
    else
      url "https://storage.googleapis.com/barn.rye.ai/releases/0.7.2/homebrew/rye-0.7.2-linux-x64-musl.tar.gz"
      sha256 "PUT_LINUX_X64_SHA256_HERE"
    end
  end

  def install
    bin.install "rye"
    bin.install "ryed"
  end

  service do
    run [opt_bin/"ryed"]
    keep_alive true
    log_path var/"log/ryed.log"
    error_log_path var/"log/ryed.err.log"
  end

  test do
    assert_match version.to_s, shell_output("#{bin}/rye version")
    assert_match "ryed", shell_output("#{bin}/ryed --version")
  end

  def caveats
    <<~EOS
      Start the daemon with:
        brew services start rye

      Then:
        rye auth login
        rye up
    EOS
  end
end
