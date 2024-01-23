from member_panel.models import NumberPointRecord, CheckboxPointRecord, \
    MultiCheckboxPointRecord, RadioPointRecord, UserInputPointRecord
from random import randint


def fill_point_records(contest_person, record_date, contest_criteria_dict):
    # Get ContestCriteria (Assuming you have these criteria created)
    number_criterion = contest_criteria_dict["number_criterion"]
    checkbox_criterion = contest_criteria_dict["checkbox_criterion"]
    multi_checkbox_criterion = contest_criteria_dict["multi_checkbox_criterion"]
    radio_criterion = contest_criteria_dict["radio_criterion"]
    user_input_criterion = contest_criteria_dict["user_input_criterion"]

    # Fill NumberPointRecord
    number_record_data = {
        'person': contest_person,
        'contest_criterion': number_criterion,
        'record_date': record_date,
        'number': randint(number_criterion.lower_bound, number_criterion.lower_bound),  # Change this value as needed,
        "point_total": number_criterion.points * randint(number_criterion.lower_bound, number_criterion.lower_bound)
    }
    NumberPointRecord.objects.create(**number_record_data)

    # Fill CheckboxPointRecord
    checkbox_record_data = {
        'person': contest_person,
        'contest_criterion': checkbox_criterion,
        'record_date': record_date,
        'checked': True,  # Change this value as needed
        "point_total": checkbox_criterion.points
    }
    CheckboxPointRecord.objects.create(**checkbox_record_data)

    # Fill MultiCheckboxPointRecord
    multi_checkbox_record_data = {
        'person': contest_person,
        'contest_criterion': multi_checkbox_criterion,
        'record_date': record_date,
        'choices': ['Option X', 'Option Y'],  # Change this value as needed
        "point_total": multi_checkbox_criterion.points
    }
    MultiCheckboxPointRecord.objects.create(**multi_checkbox_record_data)

    # Fill RadioPointRecord
    radio_record_data = {
        'person': contest_person,
        'contest_criterion': radio_criterion,
        'record_date': record_date,
        'choice': 'Option P',  # Change this value as needed
        "point_total": radio_criterion.points
    }
    RadioPointRecord.objects.create(**radio_record_data)

    # Fill UserInputPointRecord
    user_input_record_data = {
        'person': contest_person,
        'contest_criterion': user_input_criterion,
        'record_date': record_date,
        'user_input': 'Sample input',  # Change this value as needed,
        "point_total": user_input_criterion.points
    }
    UserInputPointRecord.objects.create(**user_input_record_data)
