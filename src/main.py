import os
import argparse
import yaml
import pandas as pd
import time
import random
from llm import GeminiClient
from agent import FinancialAgent

def load_config(config_path):
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    full_path = os.path.join(project_root, config_path)
    
    with open(full_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

def run(config_path):
    cfg = load_config(config_path)
    print(f"🚀 Starting Simulation: {cfg['scenario_name']}")
    
    # Init Components
    client = GeminiClient()
    agents = [
        FinancialAgent(i, cfg['system_prompt'], client) 
        for i in range(cfg['total_agents'])
    ]
    
    # Initial State
    price = cfg['initial_price']
    agents[0].receive_message(cfg['initial_rumor'])
    history = []

    # Simulation Loop
    for r in range(cfg['total_rounds']):
        print(f"\n--- Round {r+1}/{cfg['total_rounds']} @ ${price:.2f} ---")
        
        if 'events' in cfg and r in cfg['events']:
            event_msg = cfg['events'][r]
            print(f"📢 [EVENT INJECTION] {event_msg}")
            for a in agents: a.receive_message(event_msg)

        buy_vol, sell_vol = 0, 0
        
        for agent in agents:
            decision = agent.act(price)
            time.sleep(1.5) # Rate limit protection
            
            if decision:
                # Log data
                record = {
                    "Round": r, "Agent": agent.id, "Price": price,
                    "Sentiment": decision['sentiment_score'],
                    "Action": decision['real_action'],
                    "Rumor": decision['mutated_rumor']
                }
                history.append(record)
                
                # Update Volumes
                if decision['real_action'] == "BUY": buy_vol += decision['real_qty']
                if decision['real_action'] == "SELL": sell_vol += decision['real_qty']
                
                # Gossip (Simplified)
                targets = random.sample(agents, 2)
                for t in targets: 
                    if t.id != agent.id: t.receive_message(decision['mutated_rumor'])

                print(f"  A{agent.id}: {decision['real_action']} | {decision['mutated_rumor'][:40]}...")

        # Price Impact
        net_flow = buy_vol - sell_vol
        price = price * (1 + net_flow * 0.005) + random.uniform(-0.5, 0.5)

    # Save
    df = pd.DataFrame(history)
    output_file = f"data/simulations/{cfg['scenario_name']}_{int(time.time())}.csv"
    df.to_csv(output_file, index=False)
    print(f"✅ Saved to {output_file}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=str, default="configs/s1_control.yaml", help="Path to scenario config")
    args = parser.parse_args()
    
    run(args.config)