import pytest

from app.core.domain.models.game import Game
from app.core.exceptions import GameNotFoundError, InvalidRawgResponseError


class TestGameService:
    GAME_NAME = "The Witcher 3"
    RAWG_ID = 3328
    DESCRIPTION = "Open world RPG."

    @pytest.mark.asyncio
    async def test_get_rawg_id_by_name_returns_rawg_id(
        self,
        mocks_for_game_service,
        game_service,
        rawg_search_games_response,
    ):
        _game_repository_mock, rawg_client_mock = mocks_for_game_service

        rawg_client_mock.search_games.return_value = rawg_search_games_response

        rawg_id = await game_service._get_rawg_id_by_name(self.GAME_NAME)

        rawg_client_mock.search_games.assert_awaited_once_with(self.GAME_NAME)
        assert rawg_id == self.RAWG_ID

    def test_build_game_from_rawg_data_returns_valid_game(self, game_service):
        game_data = {
            "id": self.RAWG_ID,
            "name": self.GAME_NAME,
            "description_raw": self.DESCRIPTION,
            "genres": [
                {"name": "RPG"},
                {"name": "Adventure"},
            ],
        }

        game = game_service._build_game_from_rawg_data(game_data)

        assert game.rawg_id == self.RAWG_ID
        assert game.name == self.GAME_NAME
        assert game.description == self.DESCRIPTION
        assert game.genres == ["RPG", "Adventure"]

    @pytest.mark.parametrize(
        "missing_id_or_name_params",
        [
            pytest.param(
                {
                    "name": "Witcher 3",
                },
                id="rawg-id-missing",
            ),
            pytest.param(
                {
                    "id": 3328,
                },
                id="name-missing",
            ),
        ],
    )
    def test_build_game_from_rawg_data_raises_error_when_id_or_name_is_missing(
        self,
        game_service,
        missing_id_or_name_params,
    ):
        with pytest.raises(InvalidRawgResponseError):
            game_service._build_game_from_rawg_data(missing_id_or_name_params)

    @pytest.mark.asyncio
    async def test_get_or_create_game_by_name_creates_game_in_db(
        self,
        mocks_for_game_service,
        game_service,
        rawg_search_games_response,
    ):
        game_repository_mock, rawg_client_mock = mocks_for_game_service

        rawg_client_mock.search_games.return_value = rawg_search_games_response

        game_repository_mock.get_game_by_rawg_id.return_value = None

        game_data = {
            "id": self.RAWG_ID,
            "name": self.GAME_NAME,
            "description_raw": self.DESCRIPTION,
            "genres": [
                {"name": "RPG"},
                {"name": "Adventure"},
            ],
        }

        rawg_client_mock.get_game.return_value = game_data
        game_repository_mock.create_game.side_effect = lambda game: game

        created_game = await game_service.get_or_create_game_by_name(self.GAME_NAME)

        assert created_game.rawg_id == self.RAWG_ID
        assert created_game.name == self.GAME_NAME
        assert created_game.description == self.DESCRIPTION
        assert created_game.genres == ["RPG", "Adventure"]

        rawg_client_mock.search_games.assert_awaited_once_with(self.GAME_NAME)
        game_repository_mock.get_game_by_rawg_id.assert_called_once_with(self.RAWG_ID)

        rawg_client_mock.get_game.assert_awaited_once_with(self.RAWG_ID)
        game_repository_mock.create_game.assert_called_once_with(created_game)

    @pytest.mark.asyncio
    async def test_get_or_create_game_by_name_returns_game_from_db(
        self,
        mocks_for_game_service,
        game_service,
        rawg_search_games_response,
    ):
        game_repository_mock, rawg_client_mock = mocks_for_game_service

        existing_game = Game(
            rawg_id=self.RAWG_ID,
            name=self.GAME_NAME,
            description=self.DESCRIPTION,
            genres=["RPG", "Adventure"],
        )

        rawg_client_mock.search_games.return_value = rawg_search_games_response

        game_repository_mock.get_game_by_rawg_id.return_value = existing_game

        searched_game = await game_service.get_or_create_game_by_name(self.GAME_NAME)

        assert searched_game is existing_game
        assert searched_game.rawg_id == self.RAWG_ID
        assert searched_game.name == self.GAME_NAME

        rawg_client_mock.search_games.assert_awaited_once_with(self.GAME_NAME)
        game_repository_mock.get_game_by_rawg_id.assert_called_once_with(self.RAWG_ID)

        rawg_client_mock.get_game.assert_not_awaited()
        game_repository_mock.create_game.assert_not_called()

    @pytest.mark.asyncio
    async def test_get_or_create_game_by_name_raises_error_when_no_games_found(
        self,
        mocks_for_game_service,
        game_service,
    ):
        game_repository_mock, rawg_client_mock = mocks_for_game_service

        rawg_client_mock.search_games.return_value = {"results": []}

        with pytest.raises(GameNotFoundError):
            await game_service.get_or_create_game_by_name("Non existing game")

        rawg_client_mock.search_games.assert_awaited_once_with("Non existing game")
        game_repository_mock.get_game_by_rawg_id.assert_not_called()

        rawg_client_mock.get_game.assert_not_awaited()
        game_repository_mock.create_game.assert_not_called()

    @pytest.mark.asyncio
    async def test_get_or_create_game_by_name_raises_error_when_rawg_id_is_missing(
        self,
        mocks_for_game_service,
        game_service,
    ):
        game_repository_mock, rawg_client_mock = mocks_for_game_service

        rawg_client_mock.search_games.return_value = {
            "results": [
                {
                    "name": self.GAME_NAME,
                    "description_raw": self.DESCRIPTION,
                }
            ]
        }

        with pytest.raises(InvalidRawgResponseError):
            await game_service.get_or_create_game_by_name(self.GAME_NAME)

        rawg_client_mock.search_games.assert_awaited_once_with(self.GAME_NAME)
        game_repository_mock.get_game_by_rawg_id.assert_not_called()

        rawg_client_mock.get_game.assert_not_awaited()
        game_repository_mock.create_game.assert_not_called()
