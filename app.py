import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

st.set_page_config(page_title="AeroFlow", layout="wide")

st.title("AeroFlow")
st.subheader("Airline Irregular Operations (IROPs) Recovery Platform")
st.write(
    "A prototype decision-support dashboard for airline disruption recovery, "
    "operational pressure monitoring, and scenario analysis."
)

st.divider()

# =========================
# SIDEBAR INPUTS
# =========================
st.sidebar.header("IROPs Scenario Inputs")

aircraft_out_of_service = st.sidebar.slider(
    "Aircraft Out of Service", 0, 20, 2
)

crew_legality_risk = st.sidebar.slider(
    "Crew Legality Risk Level", 0, 10, 4
)

weather_disruption = st.sidebar.selectbox(
    "Weather Disruption Level",
    ["None", "Low", "Moderate", "High"]
)

avg_delay_minutes = st.sidebar.slider(
    "Average Delay Minutes", 0, 300, 45
)

passenger_misconnections = st.sidebar.slider(
    "Projected Passenger Misconnections", 0, 500, 60
)

gate_congestion = st.sidebar.slider(
    "Gate Congestion Level", 0, 10, 3
)

maintenance_events = st.sidebar.slider(
    "Maintenance Events", 0, 15, 1
)

reserve_crew_availability = st.sidebar.slider(
    "Reserve Crew Availability (%)", 0, 100, 65
)

hub_pressure = st.sidebar.slider(
    "Hub Pressure Level", 0, 10, 4
)

# =========================
# SCORING LOGIC
# =========================
disruption_score = 0

disruption_score += aircraft_out_of_service * 5
disruption_score += crew_legality_risk * 5
disruption_score += min(avg_delay_minutes * 0.12, 25)
disruption_score += min(passenger_misconnections * 0.06, 20)
disruption_score += gate_congestion * 3
disruption_score += maintenance_events * 4
disruption_score += hub_pressure * 3

if weather_disruption == "None":
    disruption_score += 0
elif weather_disruption == "Low":
    disruption_score += 8
elif weather_disruption == "Moderate":
    disruption_score += 18
else:
    disruption_score += 30

if reserve_crew_availability >= 80:
    disruption_score -= 10
elif reserve_crew_availability >= 60:
    disruption_score -= 4
elif reserve_crew_availability >= 40:
    disruption_score += 5
else:
    disruption_score += 15

disruption_score = max(0, min(100, int(disruption_score)))

# Status and recommendation
if disruption_score < 35:
    irops_status = "STABLE"
    top_action = "Maintain monitoring and preserve recovery flexibility."
elif disruption_score < 70:
    irops_status = "RECOVERY NEEDED"
    top_action = "Review aircraft swaps, reserve crews, and downstream delay exposure now."
else:
    irops_status = "IROPs CRITICAL"
    top_action = "Immediate network recovery intervention and prioritization are required."

# Derived values
flights_impacted = int((avg_delay_minutes * 0.8) + (aircraft_out_of_service * 6) + (gate_congestion * 2))
crew_alerts = int((crew_legality_risk * 2) + max(0, 5 - reserve_crew_availability / 20))
projected_cancellations = int((aircraft_out_of_service * 0.8) + (maintenance_events * 0.6) + (disruption_score / 25))
stations_under_pressure = int(1 + hub_pressure / 2 + gate_congestion / 3)

# =========================
# RECOVERY PRIORITIES
# =========================
priorities = []

if aircraft_out_of_service >= 3:
    priorities.append("Evaluate aircraft swaps or reduce low-priority flying.")
if crew_legality_risk >= 6:
    priorities.append("Review reserve crew options and legality-sensitive pairings.")
if weather_disruption in ["Moderate", "High"]:
    priorities.append("Coordinate proactive weather recovery planning across hub banks.")
if avg_delay_minutes >= 60:
    priorities.append("Protect the highest downstream-value departures first.")
if passenger_misconnections >= 100:
    priorities.append("Escalate customer reaccommodation and connection protection.")
if gate_congestion >= 6:
    priorities.append("Review gate utilization and reflow gate assignments.")
if maintenance_events >= 3:
    priorities.append("Coordinate maintenance recovery and spare aircraft planning.")
if reserve_crew_availability <= 40:
    priorities.append("Preserve remaining reserve coverage for the most critical flights.")

if not priorities:
    priorities.append("Maintain current monitoring and preserve operational flexibility.")

# =========================
# TABS / SCREENS
# =========================
tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
    "Overview",
    "Scenario Builder",
    "Delay Cascade",
    "Recovery Comparison",
    "Recovery Priorities",
    "Network Impact",
    "Decision Log"
])

# =========================
# TAB 1 — OVERVIEW
# =========================
with tab1:
    st.markdown("## Executive Overview Dashboard")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Disruption Score", f"{disruption_score}/100")
    c2.metric("IROPs Status", irops_status)
    c3.metric("Flights Impacted", flights_impacted)
    c4.metric("Projected Cancellations", projected_cancellations)

    c5, c6, c7, c8 = st.columns(4)
    c5.metric("Aircraft Out", aircraft_out_of_service)
    c6.metric("Crew Alerts", crew_alerts)
    c7.metric("Misconnections", passenger_misconnections)
    c8.metric("Stations Under Pressure", stations_under_pressure)

    st.markdown("### Top Action")
    st.info(top_action)

    overview_df = pd.DataFrame({
        "Factor": [
            "Aircraft",
            "Crew Legality",
            "Weather",
            "Delay",
            "Misconnections",
            "Gates",
            "Maintenance",
            "Hub Pressure",
            "Reserve Crew"
        ],
        "Impact": [
            aircraft_out_of_service * 5,
            crew_legality_risk * 5,
            0 if weather_disruption == "None" else 8 if weather_disruption == "Low" else 18 if weather_disruption == "Moderate" else 30,
            min(avg_delay_minutes * 0.12, 25),
            min(passenger_misconnections * 0.06, 20),
            gate_congestion * 3,
            maintenance_events * 4,
            hub_pressure * 3,
            -10 if reserve_crew_availability >= 80 else -4 if reserve_crew_availability >= 60 else 5 if reserve_crew_availability >= 40 else 15
        ]
    })

    fig, ax = plt.subplots()
    ax.bar(overview_df["Factor"], overview_df["Impact"])
    ax.set_ylabel("Impact")
    ax.set_title("IROPs Disruption Drivers")
    plt.xticks(rotation=30, ha="right")
    st.pyplot(fig)

# =========================
# TAB 2 — SCENARIO BUILDER
# =========================
with tab2:
    st.markdown("## Scenario Builder")

    scenario_df = pd.DataFrame({
        "Input": [
            "Aircraft Out of Service",
            "Crew Legality Risk",
            "Weather Disruption",
            "Average Delay Minutes",
            "Passenger Misconnections",
            "Gate Congestion",
            "Maintenance Events",
            "Reserve Crew Availability",
            "Hub Pressure"
        ],
        "Current Value": [
            aircraft_out_of_service,
            crew_legality_risk,
            weather_disruption,
            avg_delay_minutes,
            passenger_misconnections,
            gate_congestion,
            maintenance_events,
            f"{reserve_crew_availability}%",
            hub_pressure
        ]
    })

    st.dataframe(scenario_df, use_container_width=True)

    st.markdown("### What this screen does")
    st.write(
        "Use the sidebar to simulate different irregular operations conditions. "
        "AeroFlow updates the disruption score, recovery priorities, and network impact in real time."
    )

# =========================
# TAB 3 — DELAY CASCADE
# =========================
with tab3:
    st.markdown("## Delay Cascade View")

    cascade_df = pd.DataFrame({
        "Stage": [
            "Initial Disruption",
            "Downline Flight Impact",
            "Crew Impact",
            "Passenger Impact",
            "Station Impact"
        ],
        "Example Outcome": [
            f"{aircraft_out_of_service} aircraft unavailable / {maintenance_events} maintenance events",
            f"{flights_impacted} flights affected by delay propagation",
            f"{crew_alerts} crew legality or coverage alerts",
            f"{passenger_misconnections} projected misconnections",
            f"{stations_under_pressure} stations under pressure"
        ]
    })

    st.dataframe(cascade_df, use_container_width=True)

    cascade_values = [
        max(5, aircraft_out_of_service * 6 + maintenance_events * 4),
        flights_impacted,
        crew_alerts * 5,
        passenger_misconnections / 5,
        stations_under_pressure * 10
    ]

    fig2, ax2 = plt.subplots()
    ax2.plot(
        ["Initial", "Flights", "Crew", "Passengers", "Stations"],
        cascade_values,
        marker="o"
    )
    ax2.set_ylabel("Impact Level")
    ax2.set_title("Delay Cascade Progression")
    st.pyplot(fig2)

# =========================
# TAB 4 — RECOVERY COMPARISON
# =========================
with tab4:
    st.markdown("## Recovery Scenario Comparison")

    current_score = disruption_score
    aircraft_swap_score = max(0, disruption_score - min(aircraft_out_of_service * 4, 15))
    reserve_crew_score = max(0, disruption_score - (10 if reserve_crew_availability < 70 else 5))
    delay_hold_score = max(0, disruption_score - min(avg_delay_minutes // 10, 10))
    selective_cancel_score = max(0, disruption_score - min(projected_cancellations * 3, 18))

    comparison_df = pd.DataFrame({
        "Scenario": [
            "Current Operation",
            "Aircraft Swap Plan",
            "Use Reserve Crew",
            "Strategic Delay Hold",
            "Selective Cancellation"
        ],
        "Estimated Disruption Score": [
            current_score,
            aircraft_swap_score,
            reserve_crew_score,
            delay_hold_score,
            selective_cancel_score
        ],
        "Estimated Benefit": [
            "Baseline",
            "Reduces aircraft-related disruption",
            "Reduces crew legality risk",
            "Protects downstream operation",
            "Cuts network spread"
        ]
    })

    st.dataframe(comparison_df, use_container_width=True)

    fig3, ax3 = plt.subplots()
    ax3.bar(comparison_df["Scenario"], comparison_df["Estimated Disruption Score"])
    ax3.set_ylabel("Estimated Disruption Score")
    ax3.set_title("Recovery Scenario Comparison")
    plt.xticks(rotation=25, ha="right")
    st.pyplot(fig3)

# =========================
# TAB 5 — RECOVERY PRIORITIES
# =========================
with tab5:
    st.markdown("## Recovery Priorities Panel")
    st.write("Recommended operational priorities based on the current scenario:")

    for i, item in enumerate(priorities, start=1):
        st.write(f"{i}. {item}")

# =========================
# TAB 6 — NETWORK IMPACT
# =========================
with tab6:
    st.markdown("## Network Impact Summary")

    network_df = pd.DataFrame({
        "Metric": [
            "Flights Impacted",
            "Projected Cancellations",
            "Crew Alerts",
            "Passenger Misconnections",
            "Stations Under Pressure"
        ],
        "Value": [
            flights_impacted,
            projected_cancellations,
            crew_alerts,
            passenger_misconnections,
            stations_under_pressure
        ]
    })

    st.dataframe(network_df, use_container_width=True)

    fig4, ax4 = plt.subplots()
    ax4.bar(network_df["Metric"], network_df["Value"])
    ax4.set_ylabel("Value")
    ax4.set_title("Network Impact Metrics")
    plt.xticks(rotation=30, ha="right")
    st.pyplot(fig4)

# =========================
# TAB 7 — DECISION LOG
# =========================
with tab7:
    st.markdown("## Ops Notes / Decision Log")

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    log_df = pd.DataFrame({
        "Field": [
            "Timestamp",
            "IROPs Status",
            "Disruption Score",
            "Top Action",
            "Flights Impacted",
            "Projected Cancellations"
        ],
        "Value": [
            timestamp,
            irops_status,
            disruption_score,
            top_action,
            flights_impacted,
            projected_cancellations
        ]
    })

    st.table(log_df)

    st.markdown("### Operator Notes")
    st.text_area(
        "Enter recovery notes, decisions taken, or next review actions:",
        placeholder="Example: Evaluate aircraft swap for Flight 212, hold reserve crew for late bank, review weather impact at hub...",
        height=180
    )

st.divider()

st.caption(
    "Disclaimer: AeroFlow is a prototype concept for demonstration purposes only. "
    "It does not use live airline operational, crew, aircraft, or passenger data."
)
