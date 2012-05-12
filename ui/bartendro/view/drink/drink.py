# -*- coding: utf-8 -*-
from werkzeug.utils import redirect
from bartendro.utils import session, render_template, render_json, expose, validate_url, url_for
from bartendro.model.drink import Drink
from bartendro.model.drink_booze import DrinkBooze
from bartendro.model.custom_drink import CustomDrink
from bartendro.model.booze import Booze, booze_types
from bartendro.model.booze import BOOZE_TYPE_UNKNOWN, BOOZE_TYPE_ALCOHOL, BOOZE_TYPE_TART, BOOZE_TYPE_SWEET
from bartendro.model.booze_group import BoozeGroup
from bartendro.model.booze_group_booze import BoozeGroupBooze
from bartendro.model.drink_name import DrinkName
from bartendro.model.dispenser import Dispenser
from bartendro import constant 

@expose('/drink/<id>')
def view(request, id):
    drink = session.query(Drink) \
                          .filter(Drink.id == id) \
                          .first() 

    boozes = session.query(Booze) \
                          .join(DrinkBooze.booze) \
                          .filter(DrinkBooze.drink_id == drink.id)

    custom_drink = session.query(CustomDrink) \
                          .filter(drink.id == CustomDrink.drink_id) \
                          .first()
    drink.process_ingredients()
    # convert size to fl oz
    drink.sugg_size = drink.sugg_size / constant.ML_PER_FL_OZ

    has_non_alcohol = False
    has_alcohol = False
    has_sweet = False
    has_tart = False
    for booze in boozes:
        if booze.type == BOOZE_TYPE_ALCOHOL: 
            has_alcohol = True
        else:
            has_non_alcohol = True
        if booze.type == BOOZE_TYPE_SWEET: has_sweet = True
        if booze.type == BOOZE_TYPE_TART: has_tart = True

    show_sweet_tart = has_sweet and has_tart
    show_strength = has_alcohol and has_non_alcohol
    show_size = 1
    show_taster = 1

    if not custom_drink:
        return render_template("drink/index", 
                               drink=drink, 
                               title=drink.name.name,
                               is_custom=0,
                               show_sweet_tart=show_sweet_tart,
                               show_strength=show_strength,
                               show_size=show_size,
                               show_taster=show_taster)

    booze_group = session.query(BoozeGroup) \
                          .join(DrinkBooze, DrinkBooze.booze_id == BoozeGroup.abstract_booze_id) \
                          .join(BoozeGroupBooze) \
                          .join(Dispenser, Dispenser.booze_id == BoozeGroupBooze.booze_id) \
                          .filter(Drink.id == id) \
                          .first()

    booze_group.booze_group_boozes = sorted(booze_group.booze_group_boozes, 
                                            key=lambda booze: booze.sequence )

    return render_template("drink/index", 
                           drink=drink, 
                           title=drink.name.name,
                           is_custom=1,
                           custom_drink=drink.custom_drink[0],
                           booze_group=booze_group,
                           show_sweet_tart=show_sweet_tart,
                           show_strength=show_strength,
                           show_size=show_size,
                           show_taster=show_taster)

@expose('/drink/sobriety')
def sobriety(request):
    return render_template("drink/sobriety")
