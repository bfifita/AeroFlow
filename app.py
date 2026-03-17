import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="AeroFlow", layout="wide")

st.title("AeroFlow")
st.subheader("Airline Irregular Operations (IROPs) Recovery Platform")
st.write(
    "A prototype tool designed to help airline operations teams evaluate disruption severity, "
    "recovery pressure, and irregular operations risk."
)

st.divider()

# Sidebar inputs
st.sidebar.header("IROPs Scenario Inputs")

aircraft_out_of_service = st.sidebar.slider(
    "Aircraft Out of Service",
    min_value=0,
    max_value=20,
    value=2
)

crew_legality_risk = st.sidebar.slider(
    "Crew Legality Risk Level",
    min_value=0,
    max_value=10,
    value=4,
    help="Higher values indicate greater risk of duty legality issues."
)

weather_disruption = st.sidebar.selectbox(
    "Weather Disruption Level",
    ["None", "Low", "Moderate", "High"]
)

avg_delay_minutes = st.sidebar.slider(
    "Average Delay Minutes",
    min_value=0,
    max_value=300,
    value=45
)

passenger_misconnections = st.sidebar.slider(
    "Projected Passenger Misconnections",
    min_value=0,
    max_value=500,
    value=60
)

# Disruption scoring
disruption_score = 0

disruption_score += aircraft_out_of_service * 6
disruption_score += crew_legality_risk * 5
disruption_score += min(avg_delay_minutes * 0.15, 25)
disruption_score += min(passenger_misconnections * 0.08, 20)

if weather_disruption == "None":
    disruption_score += 0
elif weather_disruption == "Low":
    disruption_score += 8
elif weather_disruption == "Moderate":
    disruption_score += 18
else:
    disruption_score += 30

disruption_score = max(0, min(100, int(disruption_score)))

# Classification
if disruption_score < 35:
    irops_status = "STABLE"
    recommendation = "Disruption pressure appears manageable. Continue monitoring and maintain recovery options."
elif disruption_score < 70:
    irops_status = "RECOVERY NEEDED"
    recommendation = "This operation is under moderate disruption pressure. Recovery actions should be evaluated now."
else:
    irops_status = "IROPs CRITICAL"
    recommendation = "This operation is experiencing major disruption pressure. Immediate recovery planning and coordination are needed."

# Layout
col1, col2 = st.columns(2)

with col1:
    st.metric("Disruption Severity Score", f"{disruption_score}/100")
    st.metric("IROPs Status", irops_status)

    st.markdown("### Recommendation")
    st.info(recommendation)

with col2:
    factor_df = pd.DataFrame({
        "Factor": [
            "Aircraft Out of Service",
            "Crew Legality Risk",
            "Weather Disruption",
            "Delay Pressure",
            "Passenger Misconnections"
        ],
        "Impact": [
            aircraft_out_of_service * 6,
            crew_legality_risk * 5,
            0 if weather_disruption == "None" else 8 if weather_disruption == "Low" else 18 if weather_disruption == "Moderate" else 30,
            min(avg_delay_minutes * 0.15, 25),
            min(passenger_misconnections * 0.08, 20)
        ]
    })

    fig, ax = plt.subplots()
    ax.bar(factor_df["Factor"], factor_df["Impact"])
    ax.set_ylabel("Disruption Impact")
    ax.set_title("IROPs Disruption Drivers")
    plt.xticks(rotation=30, ha="right")
    st.pyplot(fig)

st.divider()

# Operational summary
st.markdown("## Operations Disruption Summary")

summary_df = pd.DataFrame({
    "Metric": [
        "Aircraft Out of Service",
        "Crew Legality Risk",
        "Weather Disruption",
        "Average Delay Minutes",
        "Projected Misconnections"
    ],
    "Value": [
        aircraft_out_of_service,
        crew_legality_risk,
        weather_disruption,
        avg_delay_minutes,
        passenger_misconnections
    ]
})

st.dataframe(summary_df, use_container_width=True)

st.divider()

# Recovery scenario analysis
st.markdown("## Recovery Scenario Comparison")

comparison_df = pd.DataFrame({
    "Scenario": [
        "Current Operation",
        "Reduced Delay Scenario",
        "No Weather Impact",
        "Improved Crew Recovery"
    ],
    "Estimated Disruption Score": [
        disruption_score,
        max(0, disruption_score - int(min(avg_delay_minutes * 0.08, 12))),
        max(0, disruption_score - (0 if weather_disruption == "None" else 8 if weather_disruption == "Low" else 18 if weather_disruption == "Moderate" else 30)),
        max(0, disruption_score - 10)
    ]
})

st.dataframe(comparison_df, use_container_width=True)

fig2, ax2 = plt.subplots()
ax2.plot(comparison_df["Scenario"], comparison_df["Estimated Disruption Score"], marker="o")
ax2.set_ylabel("Estimated Disruption Score")
ax2.set_title("IROPs Recovery Scenario Comparison")
st.pyplot(fig2)

st.divider()

# Recovery priorities
st.markdown("## Recovery Priorities")

priorities = []

if aircraft_out_of_service >= 3:
    priorities.append("Evaluate aircraft swaps or schedule consolidation.")
if crew_legality_risk >= 6:
    priorities.append("Review crew legality and reserve crew coverage options.")
if weather_disruption in ["Moderate", "High"]:
    priorities.append("Coordinate proactively for weather-related disruption recovery.")
if avg_delay_minutes >= 60:
    priorities.append("Prioritize flights with highest downstream delay impact.")
if passenger_misconnections >= 100:
    priorities.append("Assess rebooking pressure and customer recovery support needs.")

if not priorities:
    priorities.append("Maintain current monitoring and preserve recovery flexibility.")

for item in priorities:
    st.write(f"- {item}")

st.caption(
    "Disclaimer: AeroFlow is a prototype concept for demonstration purposes only. "
    "It does not use live airline operational, crew, or passenger data."
)
