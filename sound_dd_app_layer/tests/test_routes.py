import pytest
from httpx import AsyncClient
from unittest.mock import AsyncMock, patch
from sound_dd_app_layer.app.main import app

@pytest.mark.asyncio
async def test_compose_soundscape():
    # Mock the Synthesis Service's DB interactions
    with patch("sound_dd_app_layer.app.services.synthesis_service.SoundscapeComposer.compose_dynamic_soundscape") as mock_compose:
        
        # Expected Mock Response
        mock_compose.return_value = {
            "location": "T. Nagar",
            "theme": "Urban Chaos",
            "tracks": [
                {"url": "http://s3/bg.wav", "volume": 0.5, "start_offset": 0, "type": "bg"}
            ]
        }
        
        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.get("/api/v1/soundscape/compose", params={"location": "T. Nagar", "theme": "Urban Chaos"})
            
        assert response.status_code == 200
        data = response.json()
        assert data["theme"] == "Urban Chaos"
        assert len(data["tracks"]) == 1