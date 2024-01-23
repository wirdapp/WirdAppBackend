from admin_panel.models import *
from random import randint


def populate_contest_criteria(contest):
    section_data_1 = {
        'label': 'Section 1',
        'position': 1,
        'contest': contest,
    }
    section_1 = Section.objects.create(**section_data_1)

    section_data_2 = {
        'label': 'Section 2',
        'position': 2,
        'contest': contest,
    }
    section_2 = Section.objects.create(**section_data_2)

    # Create ContestCriteria
    # NumberCriterion
    number_criterion_data = {
        'label': 'Number Criterion',
        'description': 'Description for Number Criterion.',
        'order_in_section': 1,
        'visible': True,
        'active': True,
        'contest': contest,
        'section': section_1,
        'points': randint(1, 10),
        'lower_bound': randint(1, 5),
        'upper_bound': randint(6, 10),
    }
    number_criterion = NumberCriterion.objects.create(**number_criterion_data)

    # CheckboxCriterion
    checkbox_criterion_data = {
        'label': 'Checkbox Criterion',
        'description': 'Description for Checkbox Criterion.',
        'order_in_section': 2,
        'visible': True,
        'active': True,
        'contest': contest,
        'section': section_1,
        'points': randint(1, 10),
        'checked_label': 'Checked',
        'unchecked_label': 'Unchecked',
    }
    checkbox_criterion = CheckboxCriterion.objects.create(**checkbox_criterion_data)

    # MultiCheckboxCriterion
    multi_checkbox_criterion_data = {
        'label': 'Multi Checkbox Criterion',
        'description': 'Description for Multi Checkbox Criterion.',
        'order_in_section': 1,
        'visible': True,
        'active': True,
        'contest': contest,
        'section': section_2,
        'points': randint(1, 10),
        'options': [
            {"id": 'xxxx', "label": "Abcd", "is_correct": True},
            {"id": 'yyyy', "label": "Wxyz", "is_correct": False},
        ],
        'partial_points': True,
    }
    multi_checkbox_criterion = MultiCheckboxCriterion.objects.create(**multi_checkbox_criterion_data)

    # RadioCriterion
    radio_criterion_data = {
        'label': 'Radio Criterion',
        'description': 'Description for Radio Criterion.',
        'order_in_section': 2,
        'visible': True,
        'active': True,
        'contest': contest,
        'section': section_2,
        'points': randint(1, 10),
        'options': [
            {"id": 'xxxx', "label": "Abcd", "is_correct": True},
            {"id": 'yyyy', "label": "Wxyz", "is_correct": False},
        ],
    }
    radio_criterion = RadioCriterion.objects.create(**radio_criterion_data)

    # UserInputCriterion
    user_input_criterion_data = {
        'label': 'User Input Criterion',
        'description': 'Description for User Input Criterion.',
        'order_in_section': 3,
        'visible': True,
        'active': True,
        'contest': contest,
        'section': section_2,
        'points': randint(1, 10),
        'allow_multiline': True,
    }
    user_input_criterion = UserInputCriterion.objects.create(**user_input_criterion_data)
    return {
        "user_input_criterion": user_input_criterion,
        "radio_criterion": radio_criterion,
        "multi_checkbox_criterion": multi_checkbox_criterion,
        "checkbox_criterion": checkbox_criterion,
        "number_criterion": number_criterion
    }


def fill_groups_data(contest):
    group_data1 = {
        'name': 'Group 1',
        "contest": contest
    }
    group_data2 = {
        'name': 'Group 2',
        "contest": contest
    }

    group1 = Group.objects.create(**group_data1)
    group2 = Group.objects.create(**group_data2)

    return group1, group2
