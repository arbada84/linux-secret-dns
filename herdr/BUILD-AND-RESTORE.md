# Herdr 한국어 UI를 빌드하고 복원하기

이 절차는 Herdr 0.9.5 전용입니다. 아래 명령은 새 장치에서 재실행해 검증하지 않았습니다. 네트워크 다운로드와 빌드는 진행 중인 자료 전송이 끝난 뒤 별도로 수행하십시오.

## 소스와 패치 준비

1. 이 설정 저장소를 받은 경로를 지정합니다.

```bash
settings_repo="$HOME/dev/linux-secret-dns"
test -f "$settings_repo/herdr/herdr-0.9.5-ko.patch"
```

2. 패치 해시를 `manifest.json`과 대조합니다.

```bash
sha256sum "$settings_repo/herdr/herdr-0.9.5-ko.patch"
```

예상 SHA-256은 `4af372ee77d5f652e9690b153680c5cf2219113eb5b705710a04e1a17d572e14`입니다.

3. 기존 작업 폴더를 덮어쓰지 않고 새 폴더에 소스를 받습니다. 패치 적용 전에 받은 소스의 `AGENTS.md`, `CONTRIBUTING.md`와 빌드 요구 사항을 읽으십시오.

```bash
git clone --branch v0.9.5 --depth 1 https://github.com/herdrdev/herdr.git "$HOME/herdr-ko-rebuild"
cd "$HOME/herdr-ko-rebuild"
test "$(git rev-parse HEAD)" = 2ecf19a92fc3a7fff75b6ce3655ef04f4625ec01
git apply --check "$settings_repo/herdr/herdr-0.9.5-ko.patch"
git apply "$settings_repo/herdr/herdr-0.9.5-ko.patch"
```

이 자료는 개인 빌드용이며 원본 프로젝트에 PR을 생성하는 절차가 아닙니다.

## 빌드와 확인

원래 빌드는 Rust 1.96.1, Zig 0.16.0과 `cargo-nextest`를 사용했습니다. `rust-toolchain.toml`의 도구 버전을 유지하십시오. Zig 0.16.0 실행 파일을 준비한 뒤 `ZIG`에 실제 경로를 지정합니다. 기존 설치에서는 도구를 작업 폴더의 `.local/`에 격리했습니다.

```bash
export ZIG="$HOME/herdr-ko/.local/tools/zig-x86_64-linux-0.16.0/zig"
"$ZIG" version
cargo build --release --locked
cargo nextest run --release --locked --config 'profile.release.package.herdr.opt-level=0' --bin herdr --test-threads 3 --no-fail-fast
```

예시 `ZIG` 경로가 없으면 새 장치의 실제 Zig 경로로 바꿉니다. 기존 빌드의 격리된 Rust를 사용하는 경우에는 다음 환경도 설정합니다. 새 장치에서 복사된 경로가 작동한다고 가정하지 마십시오.

```bash
export CARGO_HOME="$HOME/herdr-ko/.local/cargo"
export RUSTUP_HOME="$HOME/herdr-ko/.local/rustup"
export PATH="$HOME/herdr-ko/.local/tools:$CARGO_HOME/bin:$PATH"
```

검사 빌드가 release 산출물을 바꿀 수 있으므로 설치용 최적화 빌드를 다시 만듭니다. 새 바이너리와 현재 서버의 버전·프로토콜 호환성을 확인합니다.

```bash
cargo build --release --locked
./target/release/herdr --version
./target/release/herdr status --json
sha256sum ./target/release/herdr
```

전체 테스트 실패 또는 `compatible=false`가 있으면 설치하지 마십시오. 다시 빌드한 바이너리가 설치 당시 해시와 같아야 한다고 가정하지 마십시오. 도구와 환경 차이로 바이너리 해시가 달라질 수 있습니다.

## 기존 파일을 백업하고 설치

현재 실행 중인 서버와 셸은 종료하지 않습니다. 호환성이 확인된 경우에만 현재 바이너리를 백업하고 새 파일을 원자적으로 교체합니다.

```bash
backup_dir="$HOME/.local/share/herdr-ko/backups/$(date +%Y%m%d-%H%M%S)"
mkdir -p "$backup_dir" "$HOME/.local/bin"
if test -f "$HOME/.local/bin/herdr"; then
	cp -p "$HOME/.local/bin/herdr" "$backup_dir/herdr"
	sha256sum "$backup_dir/herdr" > "$backup_dir/SHA256SUMS"
fi
install -m 0755 ./target/release/herdr "$HOME/.local/bin/herdr.new"
mv "$HOME/.local/bin/herdr.new" "$HOME/.local/bin/herdr"
"$HOME/.local/bin/herdr" status --json
```

`config.toml.example`을 기존 설정 파일 전체에 덮어쓰지 마십시오. 필요한 `onboarding = false` 항목만 병합합니다. 메뉴 등록 예시는 `desktop/herdr.desktop.example`에 있습니다. `Exec=herdr`와 `TryExec=herdr`가 동작하려면 데스크톱 로그인 환경의 PATH에서 Herdr를 찾아야 합니다. 현재 노트북의 메뉴 등록 파일은 `~/.local/bin/herdr`의 실제 절대 경로를 사용합니다.

## 이전 바이너리로 복원

백업 파일을 먼저 해시 기록과 대조합니다. 아래 `backup_dir`은 실제 백업 폴더로 지정합니다.

```bash
test -f "$backup_dir/herdr"
sha256sum -c "$backup_dir/SHA256SUMS"
install -m 0755 "$backup_dir/herdr" "$HOME/.local/bin/herdr.restore"
mv "$HOME/.local/bin/herdr.restore" "$HOME/.local/bin/herdr"
"$HOME/.local/bin/herdr" status --json
```

최초 공식 0.9.5 바이너리의 노트북 보관 위치는 `~/.local/share/herdr-ko/herdr-0.9.5-original`입니다. 해시는 `manifest.json`의 `original_binary_sha256`에 있습니다. 이 저장소에는 바이너리를 포함하지 않았습니다.
