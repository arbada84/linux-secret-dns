use super::*;

fn text(state: &mut ClientShellState, cols: u16, rows: u16) -> String {
    let frame = state.compose(cols, rows).expect("Korean UI frame");
    frame_rows(&frame).join("\n")
}

#[test]
fn korean_ui_keeps_menus_settings_and_help_usable_at_multiple_sizes() {
    for (cols, rows) in [(106, 30), (80, 24), (44, 30)] {
        let mut state = ClientShellState::new(ClientShellConfig::from_config(&Config::default()));
        state.set_snapshot(Box::new(snapshot()));
        state.set_pane_surface(surface());
        let screen = text(&mut state, cols, rows);
        assert!(screen.contains("client-shell"));

        state.open_settings_overlay();
        let screen = text(&mut state, cols, rows);
        assert!(screen.contains("설정"));
        assert!(screen.contains("테마"));
        assert!(screen.contains("닫기"));
        let close = state.hits.overlay_cancel;
        assert!(close.width >= 10);
        assert!(close.right() <= cols);

        state.overlay = Some(ClientShellOverlay::Help(ClientHelpOverlay {
            query: TextEditor::from("작업공간"),
            search_focused: false,
            scroll: 0,
        }));
        let screen = text(&mut state, cols, rows);
        assert!(screen.contains("작업공간"));
        assert!(!screen.contains("일치하는 단축키가 없습니다"));
    }
}
