import pytest

from app.core.domain.models.game import Game
from app.core.domain.schemas.game import GameSearchResult
from app.core.exceptions import GameNotFoundError, InvalidRawgResponseError


class TestGameService:
    GAME_NAME = "The Witcher 3"
    RAWG_ID = 3328
    DESCRIPTION = "Open world RPG."


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
    async def test_search_games_from_rawg_returns_valid_list(
        self,
        mocks_for_game_service,
        game_service,
        rawg_search_games_response,
    ):
        _game_repository_mock, rawg_client_mock = mocks_for_game_service

        rawg_client_mock.search_games.return_value = rawg_search_games_response

        result = await game_service.search_games_from_rawg(query=self.GAME_NAME)

        assert isinstance(result, list)
        assert len(result) == 2

        assert isinstance(result[0], GameSearchResult)
        assert result[0].rawg_id == self.RAWG_ID
        assert result[0].name == self.GAME_NAME
        assert result[0].released == "2015-05-18"

        rawg_client_mock.search_games.assert_awaited_once_with(query=self.GAME_NAME)

    @pytest.mark.asyncio
    async def test_search_games_from_rawg_returns_empty_list_when_no_search_results(
        self,
        mocks_for_game_service,
        game_service,
    ):
        _game_repository_mock, rawg_client_mock = mocks_for_game_service

        rawg_client_mock.search_games.return_value = {"results": []}

        result = await game_service.search_games_from_rawg(query=self.GAME_NAME)

        assert result == []

        rawg_client_mock.search_games.assert_awaited_once_with(query=self.GAME_NAME)

    @pytest.mark.asyncio
    async def test_get_or_create_game_by_rawg_id_returns_game_from_db(
        self,
        mocks_for_game_service,
        game_service,
    ):
        game_repository_mock, rawg_client_mock = mocks_for_game_service

        existing_game = Game(
            rawg_id=self.RAWG_ID,
            name=self.GAME_NAME,
            description=self.DESCRIPTION,
            genres=["RPG", "Adventure"],
        )

        game_repository_mock.get_game_by_rawg_id.return_value = existing_game

        game_from_db = await game_service.get_or_create_game_by_rawg_id(self.RAWG_ID)

        assert game_from_db is existing_game

        game_repository_mock.get_game_by_rawg_id.assert_called_once_with(self.RAWG_ID)
        rawg_client_mock.get_game.assert_not_awaited()
        game_repository_mock.create_game.assert_not_called()

    @pytest.mark.asyncio
    async def test_get_or_create_game_by_rawg_id_creates_game_when_not_already_in_db(
        self,
        mocks_for_game_service,
        game_service,
    ):
        game_repository_mock, rawg_client_mock = mocks_for_game_service

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

        created_game = await game_service.get_or_create_game_by_rawg_id(self.RAWG_ID)

        saved_game = game_repository_mock.create_game.call_args.args[0]

        assert created_game.rawg_id == self.RAWG_ID
        assert created_game.name == self.GAME_NAME
        assert created_game.description == self.DESCRIPTION
        assert created_game.genres == ["RPG", "Adventure"]

        game_repository_mock.get_game_by_rawg_id.assert_called_once_with(self.RAWG_ID)
        rawg_client_mock.get_game.assert_awaited_once_with(self.RAWG_ID)
        game_repository_mock.create_game.assert_called_once_with(created_game)

        assert saved_game is created_game
        assert saved_game.rawg_id == self.RAWG_ID
        assert saved_game.name == self.GAME_NAME
        