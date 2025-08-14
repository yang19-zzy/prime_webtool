# app/utils/option_loader.py

from app.models import FormOptions
from collections import defaultdict


def load_form_options():
    options = FormOptions.query.order_by(
        FormOptions.field_name, FormOptions.item_num
    ).all()
    grouped = defaultdict(list)
    device_map = defaultdict(list)

    for opt in options:
        if opt.field_name == "device":
            device_map[opt.value].append(opt.item_num)
        elif opt.value not in grouped[opt.field_name]:
            grouped[opt.field_name].append(opt.value)
    grouped["device"] = device_map
    return grouped
