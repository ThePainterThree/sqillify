from slack_options import (
    EXPERIENCE_LEVELS,
    MATCH_FREQUENCIES,
    load_skills,
)


def make_option(label, value):
    return {
        "text": {
            "type": "plain_text",
            "text": label,
        },
        "value": value,
    }


def build_experience_options():
    return [
        make_option(label, value)
        for label, value in EXPERIENCE_LEVELS
    ]


def build_skill_options():
    return [
        make_option(skill.title(), skill)
        for skill in load_skills()
    ]


def build_frequency_options():
    return [
        make_option(label, value)
        for label, value in MATCH_FREQUENCIES
    ]


def build_preferences_modal():
    return {
        "type": "modal",
        "callback_id": "sqillify_preferences",
        "title": {
            "type": "plain_text",
            "text": "Sqillify",
        },
        "submit": {
            "type": "plain_text",
            "text": "Save",
        },
        "close": {
            "type": "plain_text",
            "text": "Cancel",
        },
        "blocks": [
            {
                "type": "input",
                "block_id": "experience",
                "label": {
                    "type": "plain_text",
                    "text": "Experience level",
                },
                "element": {
                    "type": "multi_static_select",
                    "action_id": "experience_levels",
                    "placeholder": {
                        "type": "plain_text",
                        "text": "Choose one or more",
                    },
                    "options": build_experience_options(),
                },
            },
            {
                "type": "input",
                "block_id": "skills",
                "label": {
                    "type": "plain_text",
                    "text": "Skills",
                },
                "element": {
                    "type": "multi_static_select",
                    "action_id": "skills_selected",
                    "placeholder": {
                        "type": "plain_text",
                        "text": "Choose your skills",
                    },
                    "options": build_skill_options(),
                },
            },
            {
                "type": "input",
                "block_id": "frequency",
                "label": {
                    "type": "plain_text",
                    "text": "Match frequency",
                },
                "element": {
                    "type": "static_select",
                    "action_id": "match_frequency",
                    "placeholder": {
                        "type": "plain_text",
                        "text": "Choose frequency",
                    },
                    "options": build_frequency_options(),
                },
            },
        ],
    }