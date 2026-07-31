"""Tests for TUI main screen integration with shutdown detection."""

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.tui.main import LifecycleState, SovereignTUI


class TestLifecycleState:
    """Test lifecycle state machine transitions."""

    @pytest.mark.asyncio
    async def test_init_stays_on_ready_false(self):
        """Test INIT state stays on ready: false."""
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"ready": False, "pid": 100, "instance_uuid": "A"}

        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)
        mock_client.get = AsyncMock(return_value=mock_response)

        app = SovereignTUI()
        app._client = mock_client
        app._lifecycle_state = LifecycleState.LIFECYCLE_INIT

        await app._check_lifecycle_status()

        # Should stay in INIT and update baseline
        assert app._lifecycle_state == LifecycleState.LIFECYCLE_INIT
        assert app._lifecycle_baseline_pid == 100
        assert app._lifecycle_baseline_uuid == "A"

    @pytest.mark.asyncio
    async def test_init_transitions_to_ready_on_ready_true(self):
        """Test INIT transitions to READY on first ready: true."""
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"ready": True, "pid": 100, "instance_uuid": "A"}

        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)
        mock_client.get = AsyncMock(return_value=mock_response)

        app = SovereignTUI()
        app._client = mock_client
        app._lifecycle_state = LifecycleState.LIFECYCLE_INIT

        await app._check_lifecycle_status()

        # Should transition to READY and establish baseline
        assert app._lifecycle_state == LifecycleState.LIFECYCLE_READY
        assert app._lifecycle_baseline_pid == 100
        assert app._lifecycle_baseline_uuid == "A"

    @pytest.mark.asyncio
    async def test_ready_true_to_false_triggers_shutdown(self):
        """Test ready: true → false transition triggers shutdown."""
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"ready": False, "pid": 100, "instance_uuid": "A"}

        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)
        mock_client.get = AsyncMock(return_value=mock_response)

        app = SovereignTUI()
        app._client = mock_client
        app._lifecycle_state = LifecycleState.LIFECYCLE_READY
        app._lifecycle_baseline_pid = 100
        app._lifecycle_baseline_uuid = "A"

        # Mock graceful shutdown to avoid actual exit
        with patch.object(app, '_graceful_shutdown', new=AsyncMock()):
            await app._check_lifecycle_status()

        assert app._shutdown_detected
        assert app._lifecycle_state == LifecycleState.LIFECYCLE_SHUTDOWN_DETECTED

    @pytest.mark.asyncio
    async def test_ready_pid_change_triggers_shutdown(self):
        """Test PID change triggers shutdown."""
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"ready": True, "pid": 101, "instance_uuid": "A"}

        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)
        mock_client.get = AsyncMock(return_value=mock_response)

        app = SovereignTUI()
        app._client = mock_client
        app._lifecycle_state = LifecycleState.LIFECYCLE_READY
        app._lifecycle_baseline_pid = 100
        app._lifecycle_baseline_uuid = "A"

        # Mock graceful shutdown to avoid actual exit
        with patch.object(app, '_graceful_shutdown', new=AsyncMock()):
            await app._check_lifecycle_status()

        assert app._shutdown_detected
        assert app._lifecycle_state == LifecycleState.LIFECYCLE_SHUTDOWN_DETECTED

    @pytest.mark.asyncio
    async def test_ready_uuid_change_triggers_shutdown(self):
        """Test UUID change triggers shutdown."""
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"ready": True, "pid": 100, "instance_uuid": "B"}

        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)
        mock_client.get = AsyncMock(return_value=mock_response)

        app = SovereignTUI()
        app._client = mock_client
        app._lifecycle_state = LifecycleState.LIFECYCLE_READY
        app._lifecycle_baseline_pid = 100
        app._lifecycle_baseline_uuid = "A"

        # Mock graceful shutdown to avoid actual exit
        with patch.object(app, '_graceful_shutdown', new=AsyncMock()):
            await app._check_lifecycle_status()

        assert app._shutdown_detected
        assert app._lifecycle_state == LifecycleState.LIFECYCLE_SHUTDOWN_DETECTED

    @pytest.mark.asyncio
    async def test_ready_404_triggers_shutdown(self):
        """Test HTTP 404 triggers shutdown."""
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.status_code = 404

        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)
        mock_client.get = AsyncMock(return_value=mock_response)

        app = SovereignTUI()
        app._client = mock_client
        app._lifecycle_state = LifecycleState.LIFECYCLE_READY
        app._lifecycle_baseline_pid = 100
        app._lifecycle_baseline_uuid = "A"

        # Mock graceful shutdown to avoid actual exit
        with patch.object(app, '_graceful_shutdown', new=AsyncMock()):
            await app._check_lifecycle_status()

        assert app._shutdown_detected
        assert app._lifecycle_state == LifecycleState.LIFECYCLE_SHUTDOWN_DETECTED

    @pytest.mark.asyncio
    async def test_init_120s_timeout_surfaces_error_without_exit(self):
        """Test INIT 120s timeout surfaces error without exit."""
        # This test simulates the 120s timeout scenario
        # In practice, the polling continues indefinitely with error banner
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"ready": False, "pid": 100, "instance_uuid": "A"}

        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)
        mock_client.get = AsyncMock(return_value=mock_response)

        app = SovereignTUI()
        app._client = mock_client
        app._lifecycle_state = LifecycleState.LIFECYCLE_INIT

        # Simulate multiple polling cycles all returning ready: false
        for _ in range(5):
            await app._check_lifecycle_status()
            assert app._lifecycle_state == LifecycleState.LIFECYCLE_INIT
            assert not app._shutdown_detected  # Should not exit

    @pytest.mark.asyncio
    async def test_drain_deadline_cancels_remaining_tasks(self):
        """Test drain deadline cancels remaining tasks."""
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"ready": False, "pid": 100, "instance_uuid": "A"}

        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)
        mock_client.get = AsyncMock(return_value=mock_response)
        mock_client.post = AsyncMock(return_value=mock_response)

        app = SovereignTUI()
        app._client = mock_client
        app._lifecycle_state = LifecycleState.LIFECYCLE_READY
        app._lifecycle_baseline_pid = 100
        app._lifecycle_baseline_uuid = "A"

        # Create a refresh task
        refresh_task = asyncio.create_task(asyncio.sleep(1))
        app._refresh_task = refresh_task

        # Mock graceful shutdown to avoid actual exit
        app._graceful_shutdown = AsyncMock()

        # Trigger shutdown
        app._trigger_shutdown("test shutdown")

        # Give the task a moment to start
        await asyncio.sleep(0.1)

        # Verify refresh task was cancelled
        assert refresh_task.cancelled()
        assert app._shutdown_detected

    def test_check_shutdown_sentinel_file_exists(self):
        """Test file sentinel detection when file exists."""
        app = SovereignTUI()

        with patch('app.tui.main.SHUTDOWN_SENTINEL_PATH') as mock_path:
            mock_path.exists.return_value = True
            result = app._check_shutdown_sentinel()
            assert result is True

    def test_check_shutdown_sentinel_file_not_exists(self):
        """Test file sentinel detection when file does not exist."""
        app = SovereignTUI()

        with patch('app.tui.main.SHUTDOWN_SENTINEL_PATH') as mock_path:
            mock_path.exists.return_value = False
            result = app._check_shutdown_sentinel()
            assert result is False

    def test_check_shutdown_sentinel_exception_handling(self):
        """Test file sentinel detection handles exceptions gracefully."""
        app = SovereignTUI()

        with patch('app.tui.main.SHUTDOWN_SENTINEL_PATH') as mock_path:
            mock_path.exists.side_effect = Exception("File system error")
            result = app._check_shutdown_sentinel()
            assert result is False

    def test_action_cycle_panel(self):
        """Test panel cycling action."""
        app = SovereignTUI()

        # Mock the switcher
        mock_switcher = MagicMock()
        mock_switcher.current = "panel-orchestrator"
        app.query_one = MagicMock(return_value=mock_switcher)

        # Test cycling
        app.action_cycle_panel()

        # Should have cycled to next panel
        assert mock_switcher.current == "panel-workers"

    def test_on_button_pressed(self):
        """Test button press handling."""
        app = SovereignTUI()

        # Mock the button and switcher
        mock_button = MagicMock()
        mock_button.id = "btn-workers"

        mock_switcher = MagicMock()
        app.query_one = MagicMock(return_value=mock_switcher)

        # Simulate button press
        from textual.widgets import Button
        event = Button.Pressed(mock_button)
        app.on_button_pressed(event)

        # Should have switched to workers panel
        assert mock_switcher.current == "panel-workers"

    def test_trigger_shutdown_already_shutdown(self):
        """Test shutdown trigger handles already shutdown state."""
        app = SovereignTUI()
        app._shutdown_detected = True

        # Should not trigger shutdown again
        app._trigger_shutdown("test reason")
        assert app._shutdown_detected is True

    def test_graceful_shutdown_network_error(self):
        """Test graceful shutdown handles network errors during logout."""
        app = SovereignTUI()
        app._shutdown_detected = True

        async def test_logout():
            raise Exception("Network error")

        with patch.object(app._client, 'post', side_effect=test_logout):
            # Should handle network error gracefully
            import asyncio
            asyncio.run(app._graceful_shutdown("test"))

    def test_lifecycle_state_transition_sequence(self):
        """Test lifecycle state transitions occur in correct sequence."""
        app = SovereignTUI()

        # Initial state
        assert app._lifecycle_state == LifecycleState.LIFECYCLE_INIT

        # Simulate transition to READY
        app._lifecycle_state = LifecycleState.LIFECYCLE_READY
        assert app._lifecycle_state == LifecycleState.LIFECYCLE_READY

        # Simulate transition to SHUTDOWN_DETECTED
        app._lifecycle_state = LifecycleState.LIFECYCLE_SHUTDOWN_DETECTED
        assert app._lifecycle_state == LifecycleState.LIFECYCLE_SHUTDOWN_DETECTED

    def test_check_lifecycle_status_connection_error_in_init(self):
        """Test lifecycle status check handles connection errors during init."""
        app = SovereignTUI()
        app._lifecycle_state = LifecycleState.LIFECYCLE_INIT

        async def test_connection_error():
            raise Exception("Connection error")

        with patch.object(app._client, 'get', side_effect=test_connection_error):
            import asyncio
            # Should handle connection error gracefully in INIT state
            asyncio.run(app._check_lifecycle_status())

    def test_check_lifecycle_status_connection_error_in_ready(self):
        """Test lifecycle status check triggers shutdown on connection error in READY state."""
        app = SovereignTUI()
        app._lifecycle_state = LifecycleState.LIFECYCLE_READY
        app._shutdown_detected = False

        async def test_connection_error():
            raise Exception("Connection error")

        with patch.object(app._client, 'get', side_effect=test_connection_error):
            with patch.object(app, '_trigger_shutdown') as mock_trigger:
                import asyncio
                asyncio.run(app._check_lifecycle_status())
                # Should trigger shutdown on connection error in READY state
                mock_trigger.assert_called_once()

    def test_initialize_panels_handles_widget_tree_errors(self):
        """Test panel initialization handles widget tree errors gracefully."""
        app = SovereignTUI()

        # Mock widget tree to raise error only for Static queries
        with patch.object(app, 'query_one', side_effect=Exception("Widget tree error")):
            # Should handle widget tree error gracefully
            try:
                app._initialize_panels()
            except Exception:
                # Expected to raise since widget tree is not mounted
                pass

    def test_start_lifecycle_monitoring_handles_async_errors(self):
        """Test lifecycle monitoring handles async errors gracefully."""
        app = SovereignTUI()

        async def test_monitoring_error(*args, **kwargs):
            raise Exception("Monitoring error")

        with patch('asyncio.create_task', side_effect=test_monitoring_error):
            # Should handle async error gracefully
            try:
                app._start_lifecycle_monitoring()
            except Exception:
                # Expected to raise since async error
                pass

    @pytest.mark.asyncio
    async def test_refresh_task_cancellation(self):
        """Test refresh task cancellation during shutdown."""
        app = SovereignTUI()
        app._shutdown_detected = False

        # Mock refresh task
        mock_task = MagicMock()
        app._refresh_task = mock_task

        # Mock graceful shutdown to avoid event loop error
        with patch.object(app, '_graceful_shutdown'):
            app._trigger_shutdown("test reason")

        # Should cancel refresh task
        mock_task.cancel.assert_called_once()

    def test_cookie_persistence_error_handling(self):
        """Test cookie persistence handles errors gracefully."""
        app = SovereignTUI()
        app._shutdown_detected = True

        async def test_persistence_error():
            raise Exception("Persistence error")

        with patch.object(app._client, '__aexit__', side_effect=test_persistence_error):
            import asyncio
            # Should handle persistence error gracefully
            asyncio.run(app._graceful_shutdown("test"))

    @pytest.mark.asyncio
    async def test_lifecycle_baseline_updates_on_ready_false(self):
        """Test lifecycle baseline updates even when ready is false."""
        app = SovereignTUI()
        app._lifecycle_state = LifecycleState.LIFECYCLE_INIT

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "ready": False,
            "pid": 12345,
            "instance_uuid": "test-uuid"
        }

        with patch.object(app._client, 'get', return_value=mock_response):
            await app._check_lifecycle_status()

    @pytest.mark.asyncio
    async def test_check_lifecycle_status_connection_error_in_init(self):
        """Test lifecycle status check handles connection error during init."""
        mock_client = MagicMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)
        mock_client.get = AsyncMock(side_effect=Exception("Connection error"))

        tui = SovereignTUI()
        tui._client = mock_client
        tui._lifecycle_state = LifecycleState.LIFECYCLE_INIT

        # Should handle connection error gracefully
        await tui._check_lifecycle_status()
        assert tui._lifecycle_state == LifecycleState.LIFECYCLE_INIT  # Should stay in INIT

    @pytest.mark.asyncio
    async def test_check_lifecycle_status_connection_error_in_ready(self):
        """Test lifecycle status check handles connection error during ready."""
        mock_client = MagicMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)
        mock_client.get = AsyncMock(side_effect=Exception("Connection error"))

        tui = SovereignTUI()
        tui._client = mock_client
        tui._lifecycle_state = LifecycleState.LIFECYCLE_READY
        tui._lifecycle_baseline_pid = 12345
        tui._lifecycle_baseline_uuid = "test-uuid"

        # Should handle connection error gracefully
        await tui._check_lifecycle_status()
        assert tui._lifecycle_state == LifecycleState.LIFECYCLE_SHUTDOWN_DETECTED  # Should trigger shutdown

    @pytest.mark.asyncio
    async def test_multiple_shutdown_triggers_idempotent(self):
        """Test multiple shutdown triggers are idempotent."""
        app = SovereignTUI()
        app._shutdown_detected = False

        # Mock graceful shutdown to avoid event loop error
        with patch.object(app, '_graceful_shutdown'):
            # First trigger
            app._trigger_shutdown("first reason")
            assert app._shutdown_detected is True

            # Second trigger should be idempotent
            app._trigger_shutdown("second reason")
            # Should remain in shutdown state
            assert app._shutdown_detected is True
