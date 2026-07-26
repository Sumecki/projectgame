import pytest

from app.core.exceptions import GameDescriptionNotAvailableError


class TestBedrockDescriptionService:
    GAME_NAME = "The Witcher 3"
    GAME_DESCRIPTION = "Geralt searches for Ciri."
    GENERATED_DESCRIPTION = "A cheap monster movie from the 1980s."

    def test_build_prompts_returns_expected_instructions_and_game_data(
        self,
        bedrock_service,
    ):
        system_prompt, user_prompt = (
            bedrock_service._build_prompts(
                game_name=self.GAME_NAME,
                game_description=self.GAME_DESCRIPTION,
            )
        )

        assert "exactly 5 sentences" in system_prompt
        assert "<example_input>" in system_prompt
        assert "<example_output>" in system_prompt
        assert "Do not include a title" in system_prompt


        assert self.GAME_NAME in user_prompt
        assert self.GAME_DESCRIPTION in user_prompt
        assert "<game_description>" in user_prompt
        assert "</game_description>" in user_prompt

    def test_extract_text_returns_generated_description(
        self,
        bedrock_service,
        bedrock_response,
    ):
        result = bedrock_service._extract_text(bedrock_response)

        assert result == self.GENERATED_DESCRIPTION

    def test_generate_text_returns_extracted_text(
        self,
        bedrock_service,
        bedrock_client_mock,
        bedrock_response,
    ):
        bedrock_client_mock.converse.return_value = bedrock_response

        result = bedrock_service._generate_text(
            system_prompt="System prompt",
            user_prompt="User prompt",
        )

        assert result == self.GENERATED_DESCRIPTION

    def test_rewrite_description_as_b_movie_plot_returns_generated_text(
        self,
        bedrock_client_mock,
        bedrock_service,
        bedrock_response,
    ):
        bedrock_client_mock.converse.return_value = bedrock_response

        result = bedrock_service.rewrite_description_as_b_movie_plot(
            game_name=self.GAME_NAME,
            game_description=self.GAME_DESCRIPTION,
        )

        assert result == self.GENERATED_DESCRIPTION
        bedrock_client_mock.converse.assert_called_once()

    def test_rewrite_description_sends_correct_request_to_bedrock(
        self,
        bedrock_client_mock,
        bedrock_service,
        bedrock_response,
    ):
        bedrock_client_mock.converse.return_value = bedrock_response

        bedrock_service.rewrite_description_as_b_movie_plot(
            game_name=self.GAME_NAME,
            game_description=self.GAME_DESCRIPTION,
        )

        bedrock_client_mock.converse.assert_called_once()

        call_arguments = bedrock_client_mock.converse.call_args.kwargs

        assert call_arguments["modelId"] == bedrock_service.model_id
        assert call_arguments["inferenceConfig"] == {
            "maxTokens": bedrock_service.max_tokens,
            "temperature": bedrock_service.temperature,
        }

        system_prompt = call_arguments["system"][0]["text"]
        user_prompt = call_arguments["messages"][0]["content"][0]["text"]

        assert "low-budget B-movies" in system_prompt
        assert self.GAME_NAME in user_prompt
        assert self.GAME_DESCRIPTION in user_prompt

    @pytest.mark.parametrize(
        "game_description",
        [
            pytest.param(None, id="description-is-none"),
            pytest.param("", id="description-is-empty"),
        ],
    )
    def test_rewrite_description_raises_error_when_description_is_missing(
        self,
        bedrock_client_mock,
        bedrock_service,
        game_description,
    ):
        with pytest.raises(
            GameDescriptionNotAvailableError,
            match="Game description is not available",
        ):
            bedrock_service.rewrite_description_as_b_movie_plot(
                game_name=self.GAME_NAME,
                game_description=game_description,
            )

        bedrock_client_mock.converse.assert_not_called()
