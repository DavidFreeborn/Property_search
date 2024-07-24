import csv
import re
from collections import Counter

def clean_agent_name(name):
    # Remove common suffixes and clean the name
    name = re.sub(r',.*$', '', name)  # Remove everything after a comma
    name = re.sub(r'\s+(Ltd|Limited|LLP|PLC|Inc|London)$', '', name, flags=re.IGNORECASE)
    return name.strip()

def group_agents(input_file, output_file, summary_file):
    agent_groups = {}
    properties = []
    grouped_agent_counts = Counter()

    with open(input_file, 'r', newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            agent = row['formattedBranchName']
            cleaned_agent = clean_agent_name(agent)
            main_agent = cleaned_agent.split()[0]  # Take the first word as the main agent

            if main_agent in agent_groups:
                agent_groups[main_agent].add(cleaned_agent)
            else:
                agent_groups[main_agent] = {cleaned_agent}

            row['groupedAgent'] = main_agent
            properties.append(row)
            grouped_agent_counts[main_agent] += 1

    # Print grouping information
    for main_agent, sub_agents in agent_groups.items():
        print(f"{main_agent}: {', '.join(sub_agents)}")

    # Write the new CSV file with grouped agents
    with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = list(properties[0].keys())
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        for prop in properties:
            writer.writerow(prop)

    print(f"\nGrouped agents saved to {output_file}")

    # Write the summary CSV file
    with open(summary_file, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Grouped Agent', 'Number of Properties'])
        for agent, count in sorted(grouped_agent_counts.items(), key=lambda x: x[1], reverse=True):
            writer.writerow([agent, count])

    print(f"Agent summary saved to {summary_file}")

# Use the function
input_file = 'rightmove_properties_streamlined.csv'
output_file = 'rightmove_properties_grouped_agents.csv'
summary_file = 'estate_agents_summary.csv'
group_agents(input_file, output_file, summary_file)
