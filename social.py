import random

DIALOGUE_DB = {
    "greet_friendly": ["Hail, friend!", "Good to see you.", "Hello there!", "Well met!", "Hi!"],
    "greet_hostile": ["Step aside.", "No time for you.", "Ugh...", "Don't test me.", "Hmph."],
    "flirt": ["You shine like the stars.", "Care for a drink?", "You have a fire in you.", "Stunning."],
    "insult": ["You look like a wet dog.", "Pathetic worm.", "Get lost.", "Coward."],
    "job_fisher": ["Fish are biting today.", "Big one got away...", "Smells like salt."],
    "job_farmer": ["Harvest will be good.", "Rain's coming.", "Hard work, honest life."]
}

def get_dialogue(key):
    return random.choice(DIALOGUE_DB.get(key, ["..."]))

def process_interaction(actor, target, manual_choice=None):
    rel = actor.get_relationship(target.name)
    target_rel = target.get_relationship(actor.name)
    
    act_type = "Chat"
    line = "..."
    
    # 1. Decision Logic
    if manual_choice:
        if manual_choice == 1: act_type = "Chat"
        elif manual_choice == 2: act_type = "Flirt"
        elif manual_choice == 3: act_type = "Insult"
    else:
        # AI Decision
        if rel.romance > 15: act_type = "Flirt" if random.random() < 0.4 else "Chat"
        elif rel.friendship < -15: act_type = "Insult"
        else: act_type = "Chat"

    # 2. Outcome Logic
    if act_type == "Chat":
        if rel.friendship >= 0:
            line = get_dialogue("greet_friendly")
            rel.friendship += 1; target_rel.friendship += 1
        else:
            line = get_dialogue("greet_hostile")
            
    elif act_type == "Flirt":
        line = get_dialogue("flirt")
        attract = (actor.stats['social'] + actor.stats['libido']) 
        standards = target.stats['intellect']
        if attract >= standards or rel.romance > 5:
            rel.romance += 4; target_rel.romance += 3
        else:
            line = "...I don't think so."
            rel.friendship -= 2
            
    elif act_type == "Insult":
        line = get_dialogue("insult")
        rel.friendship -= 5; target_rel.friendship -= 8
        target_rel.status = "Enemy"

    # Update Status Labels
    for r in [rel, target_rel]:
        if r.status != "Exes":
            if r.romance > 40: r.status = "Lover"
            elif r.romance > 20: r.status = "Crush"
            elif r.friendship > 40: r.status = "Bestie"
            elif r.friendship < -20: r.status = "Enemy"

    return act_type, line