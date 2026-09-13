import { useMemo, useState } from 'react'

import { ApiError } from '@/api/errors'
import { PageEmptyState } from '@/components/PageEmptyState'
import { PageErrorState } from '@/components/PageErrorState'
import { PageLoadingState } from '@/components/PageLoadingState'
import { useCreateRiskEvaluation } from '@/features/profile/hooks/useCreateRiskEvaluation'
import { useRiskQuestionnaire } from '@/features/profile/hooks/useRiskQuestionnaire'

interface RiskQuestionnaireProps {
  onCancel?: () => void
  onCompleted: () => void
}

function getErrorMessage(error: Error): string {
  if (error instanceof ApiError) {
    if (error.status === 409) {
      return 'La evaluación no pudo registrarse porque existe un conflicto con el estado actual de tu perfil.'
    }

    if (error.status === 422) {
      return 'Las respuestas enviadas no son válidas. Revisa el cuestionario e inténtalo nuevamente.'
    }

    if (error.status === 404) {
      return 'El cuestionario ya no se encuentra disponible.'
    }

    if (error.status !== undefined && error.status >= 500) {
      return 'El servidor no pudo procesar la evaluación. Inténtalo nuevamente.'
    }
  }

  return error.message
}

export function RiskQuestionnaire({ onCancel, onCompleted }: RiskQuestionnaireProps) {
  const questionnaireQuery = useRiskQuestionnaire()
  const evaluationMutation = useCreateRiskEvaluation()

  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0)
  const [answers, setAnswers] = useState<Record<string, string>>({})

  const questions = useMemo(
    () => [...(questionnaireQuery.data?.preguntas ?? [])].sort((a, b) => a.orden - b.orden),
    [questionnaireQuery.data],
  )

  if (questionnaireQuery.isPending) {
    return <PageLoadingState message="Cargando cuestionario de perfil de riesgo..." />
  }

  if (questionnaireQuery.isError) {
    return (
      <PageErrorState
        title="No fue posible cargar el cuestionario"
        message={questionnaireQuery.error.message}
        onRetry={() => {
          void questionnaireQuery.refetch()
        }}
      />
    )
  }

  const questionnaire = questionnaireQuery.data

  if (!questionnaire || questions.length === 0) {
    return (
      <PageEmptyState
        title="No hay un cuestionario disponible"
        description="Actualmente no existen preguntas publicadas para realizar tu evaluación."
      />
    )
  }

  const unsupportedQuestion = questions.find((question) => question.tipo !== 'OPCION_UNICA')

  if (unsupportedQuestion) {
    return (
      <PageErrorState
        title="El cuestionario contiene un tipo de pregunta no compatible"
        message={`La pregunta ${unsupportedQuestion.orden} utiliza el tipo ${unsupportedQuestion.tipo}.`}
      />
    )
  }

  const currentQuestion = questions[currentQuestionIndex]

  if (!currentQuestion) {
    return (
      <PageErrorState
        title="No fue posible mostrar el cuestionario"
        message="La pregunta solicitada no se encuentra disponible."
      />
    )
  }

  const options = [...(currentQuestion.opciones ?? [])].sort((a, b) => a.orden - b.orden)
  const selectedOptionId = answers[currentQuestion.id]
  const isLastQuestion = currentQuestionIndex === questions.length - 1
  const canContinue = !currentQuestion.obligatoria || Boolean(selectedOptionId)

  function selectAnswer(optionId: string) {
    setAnswers((currentAnswers) => ({
      ...currentAnswers,
      [currentQuestion.id]: optionId,
    }))
  }

  function goToPreviousQuestion() {
    setCurrentQuestionIndex((index) => Math.max(0, index - 1))
  }

  function goToNextQuestion() {
    if (!canContinue) {
      return
    }

    setCurrentQuestionIndex((index) => Math.min(questions.length - 1, index + 1))
  }

  async function submitEvaluation() {
    if (!canContinue || evaluationMutation.isPending) {
      return
    }

    const unansweredRequiredQuestion = questions.find(
      (question) => question.obligatoria && !answers[question.id],
    )

    if (unansweredRequiredQuestion) {
      const unansweredIndex = questions.findIndex(
        (question) => question.id === unansweredRequiredQuestion.id,
      )

      setCurrentQuestionIndex(unansweredIndex)
      return
    }

    const evaluationAnswers = questions.flatMap((question) => {
      const optionId = answers[question.id]

      if (!optionId) {
        return []
      }

      return [
        {
          question_id: question.id,
          option_id: optionId,
        },
      ]
    })

    try {
      await evaluationMutation.mutateAsync({
        questionnaire_id: questionnaire.id,
        answers: evaluationAnswers,
      })

      onCompleted()
    } catch {
      // React Query conserva el error en evaluationMutation.error
      // y la interfaz lo presenta al usuario.
    }
  }

  return (
    <section className="risk-questionnaire" aria-labelledby="risk-questionnaire-title">
      <header className="risk-questionnaire__header">
        <div>
          <p className="app__eyebrow">Evaluación de riesgo</p>
          <h2 id="risk-questionnaire-title">{questionnaire.nombre}</h2>

          {questionnaire.descripcion ? (
            <p className="risk-questionnaire__description">{questionnaire.descripcion}</p>
          ) : null}
        </div>

        <span className="risk-questionnaire__version">Versión {questionnaire.version}</span>
      </header>

      <div className="risk-questionnaire__progress">
        <div className="risk-questionnaire__progress-heading">
          <span>
            Pregunta {currentQuestionIndex + 1} de {questions.length}
          </span>

          <span>{Math.round(((currentQuestionIndex + 1) / questions.length) * 100)} %</span>
        </div>

        <progress value={currentQuestionIndex + 1} max={questions.length}>
          {currentQuestionIndex + 1} de {questions.length}
        </progress>
      </div>

      <fieldset className="risk-questionnaire__question">
        <legend>
          <span className="risk-questionnaire__question-number">
            Pregunta {currentQuestion.orden}
          </span>

          {currentQuestion.texto}
        </legend>

        <div className="risk-questionnaire__options">
          {options.map((option) => {
            const checked = selectedOptionId === option.id

            return (
              <label
                className={`risk-questionnaire__option${
                  checked ? ' risk-questionnaire__option--selected' : ''
                }`}
                key={option.id}
              >
                <input
                  type="radio"
                  name={`question-${currentQuestion.id}`}
                  value={option.id}
                  checked={checked}
                  onChange={() => {
                    selectAnswer(option.id)
                  }}
                />

                <span>{option.texto}</span>
              </label>
            )
          })}
        </div>
      </fieldset>

      {currentQuestion.obligatoria && !selectedOptionId ? (
        <p className="risk-questionnaire__validation" role="status">
          Selecciona una respuesta para continuar.
        </p>
      ) : null}

      {evaluationMutation.isError ? (
        <div className="risk-questionnaire__error" role="alert">
          <strong>No fue posible registrar la evaluación.</strong>
          <span>{getErrorMessage(evaluationMutation.error)}</span>
        </div>
      ) : null}

      <div className="risk-questionnaire__actions">
        <div>
          {onCancel ? (
            <button
              className="button button--secondary"
              type="button"
              onClick={onCancel}
              disabled={evaluationMutation.isPending}
            >
              Cancelar
            </button>
          ) : null}
        </div>

        <div className="risk-questionnaire__navigation">
          <button
            className="button button--secondary"
            type="button"
            onClick={goToPreviousQuestion}
            disabled={currentQuestionIndex === 0 || evaluationMutation.isPending}
          >
            Anterior
          </button>

          {isLastQuestion ? (
            <button
              className="button button--primary"
              type="button"
              onClick={() => {
                void submitEvaluation()
              }}
              disabled={!canContinue || evaluationMutation.isPending}
            >
              {evaluationMutation.isPending ? 'Calculando perfil...' : 'Finalizar evaluación'}
            </button>
          ) : (
            <button
              className="button button--primary"
              type="button"
              onClick={goToNextQuestion}
              disabled={!canContinue || evaluationMutation.isPending}
            >
              Siguiente
            </button>
          )}
        </div>
      </div>
    </section>
  )
}
