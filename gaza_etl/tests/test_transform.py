import pytest, json, sys
from pathlib import Path
from unittest.mock import patch, MagicMock, mock_open, call
from extract_hdxapi import Extract



class TestDownloadAllUrls:

    def _make_mock_response(self, chunks=None):
        """Fabrique de mock HTTP réutilisable."""
        mock_resp = MagicMock()
        mock_resp.iter_content.return_value = chunks or [b"data1", b"data2"]    
        mock_resp.raise_for_status.return_value = None
        # Gestion du context manager "with requests.get() as r"
        mock_resp.__enter__ = MagicMock(return_value=mock_resp)
        mock_resp.__exit__ = MagicMock(return_value=False)
        return mock_resp

    @patch("extract_hdxapi.requests.get")
    @patch("builtins.open", new_callable=mock_open, 
           read_data=json.dumps([{"download_url": "https://hdx.fake/pop.csv"}]))
    def test_telecharge_un_fichier(self, mock_file, mock_get):
        """Cas nominal : 1 URL dans le JSON → 1 fichier téléchargé."""
        mock_get.return_value = self._make_mock_response()

        Extract.downloadFiles(results_file="fake_results.json", zone_geographique = "thailand")

        mock_get.assert_called_once_with("https://hdx.fake/pop.csv", stream=True)
        mock_file().write.assert_called()

    @patch("extract_hdxapi.requests.get")
    @patch("builtins.open", new_callable=mock_open,
           read_data=json.dumps([
               {"download_url": "https://hdx.fake/pop.csv"},
               {"download_url": "https://hdx.fake/shelter.csv"}
           ]))
    def test_telecharge_plusieurs_fichiers(self, mock_file, mock_get):
        """Cas nominal : 2 URLs → requests.get appelé 2 fois."""
        mock_get.return_value = self._make_mock_response()

        Extract.downloadFiles(results_file="fake_results.json", zone_geographique = "thailand")

        assert mock_get.call_count == 2

    @patch("extract_hdxapi.requests.get")
    @patch("builtins.open", new_callable=mock_open,
           read_data=json.dumps([{"download_url": "https://hdx.fake/pop.csv"}]))
    def test_erreur_http(self, mock_file, mock_get):
        """Cas d'erreur : serveur KO → exception levée."""
        mock_resp = self._make_mock_response()
        mock_resp.raise_for_status.side_effect = Exception("503 Service Unavailable")
        mock_get.return_value = mock_resp

        with pytest.raises(Exception, match="503"):
            Extract.downloadFiles(results_file="fake_results.json", zone_geographique = "thailand")

    @patch("extract_hdxapi.requests.get")
    @patch("builtins.open", new_callable=mock_open,
           read_data=json.dumps([{"download_url": None}]))
    def test_url_nulle(self, mock_file, mock_get):
        """Edge case : download_url est None → pas d'appel HTTP."""
        Extract.downloadFiles(results_file="fake_results.json", zone_geographique = "thailand")

        mock_get.assert_not_called()