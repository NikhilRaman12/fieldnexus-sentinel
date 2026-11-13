"""
environment_adapter.py — bridge between raw Kaggle env and our typed layer.
Provides the EnvironmentAdapter class used by main.py.
"""
from __future__ import annotations
from typing import Any, Dict, Optional
from .schema import GameState, GameConfig
from .state_parser import StateParser
from .action_space import Action


class EnvironmentAdapter:
    """Stateful adapter that maps Kaggle obs→GameState and Action→dict."""

    def __init__(self):
        self._parser = StateParser()
        self._config_loaded = False

    def on_config(self, raw_config: Any) -> None:
        """Call once when episode config is available."""
        self._parser.update_config(raw_config)
        self._config_loaded = True

    def parse_observation(self, obs: Any, raw_config: Any = None) -> GameState:
        """Convert raw observation to GameState."""
        if raw_config is not None and not self._config_loaded:
            self.on_config(raw_config)
        return self._parser.parse(obs, raw_config)

    def action_to_dict(self, action: Action) -> Dict[str, Any]:
        """Convert typed Action to the raw dict the environment expects."""
        return action.to_dict()

    @property
    def config(self) -> GameConfig:
        return self._parser.config
