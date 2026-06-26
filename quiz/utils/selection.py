import random
from ..models import QuestionGroup, Question


def select_questions_for_session(quiz, session_id_seed):
    """
    Select questions for a student session using stratified sampling from groups.
    - If groups exist with pick_count, pick that many from each group.
    - Otherwise fallback to all questions (shuffled if randomize_questions).
    Returns list of Question objects in the order to present.
    Deterministic per session using seed derived from session_id.
    """
    random.seed(session_id_seed)

    questions = []

    groups = list(quiz.groups.order_by('order'))
    if groups:
        for group in groups:
            pool = list(group.questions.all())
            pick = min(group.pick_count, len(pool))
            if pick > 0:
                picked = random.sample(pool, pick)
                # sort picked by their order for stability within group
                picked.sort(key=lambda q: q.order)
                questions.extend(picked)
    else:
        # No groups: use all questions
        questions = list(quiz.questions.all().order_by('order'))

    if quiz.randomize_questions:
        random.shuffle(questions)

    random.seed()  # reset
    return questions


def compute_max_score(questions):
    """Sum marks for list of selected questions"""
    return sum(q.marks for q in questions)
