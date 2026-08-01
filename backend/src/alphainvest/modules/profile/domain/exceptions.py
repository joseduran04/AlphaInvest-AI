class ProfileError(Exception):
    """Excepción base del módulo de perfil de riesgo."""


class QuestionnaireNotFoundError(ProfileError):
    """No existe un cuestionario activo o publicado."""


class IncompleteQuestionnaireError(ProfileError):
    """La evaluación no contiene todas las respuestas obligatorias."""


class InvalidAnswerError(ProfileError):
    """Una respuesta no pertenece a la pregunta indicada."""


class DuplicateAnswerError(ProfileError):
    """La evaluación contiene más de una respuesta para la misma pregunta."""


class RiskProfileNotFoundError(ProfileError):
    """El usuario todavía no cuenta con un perfil de riesgo."""


class EvaluationNotFoundError(ProfileError):
    """La evaluación solicitada no existe."""