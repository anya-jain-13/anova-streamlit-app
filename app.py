import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import statsmodels.api as sm
import statsmodels.formula.api as smf
from statsmodels.stats.multicomp import pairwise_tukeyhsd

st.set_page_config(page_title="ANOVA Project", layout="wide")

st.title("🚗 Accident Severity Analysis using ANOVA")

st.write("Upload your Excel dataset to begin analysis")

# Upload Excel
file = st.file_uploader("Upload Excel File", type=["xlsx"])

if file is not None:

    df = pd.read_excel(file)

    st.subheader("📊 Dataset Preview")
    st.write(df.head())

    st.subheader("🔍 Select Variables")

    # Target variable
    target = st.selectbox("Select Target Variable (Numeric)", df.columns)

    # Multiple factor variables
    factors = st.multiselect("Select Factor Variables", df.columns)

    # Interaction option
    interaction = st.checkbox("Include Interaction Effects")

    # ---------------- ANOVA ---------------- #
    if st.button("Run ANOVA"):
        try:
            if len(factors) == 0:
                st.warning("Please select at least one factor variable")
            else:
                # Convert to categorical
                for col in factors:
                    df[col] = df[col].astype("category")

                # Formula creation
                if interaction:
                    formula = f"{target} ~ " + " * ".join([f"C({f})" for f in factors])
                else:
                    formula = f"{target} ~ " + " + ".join([f"C({f})" for f in factors])

                model = smf.ols(formula, data=df).fit()
                anova_table = sm.stats.anova_lm(model, typ=2)

                st.subheader("📈 ANOVA Result")
                st.write(anova_table)

                # Interpretation
                st.subheader("🧠 Interpretation")

                significant = anova_table[anova_table["PR(>F)"] < 0.05]

                if not significant.empty:
                    for index in significant.index:
                        st.success(f"👉 {index} significantly affects {target}")
                else:
                    st.warning("👉 No significant factors found")

        except Exception as e:
            st.error(f"❌ Error: {e}")

    # ---------------- Tukey ---------------- #
    if st.button("Run Tukey Test"):
        try:
            if len(factors) == 0:
                st.warning("Select one factor for Tukey test")
            else:
                factor = factors[0]

                tukey = pairwise_tukeyhsd(endog=df[target],
                                         groups=df[factor],
                                         alpha=0.05)

                st.subheader("📊 Tukey Test Result")
                st.text(tukey.summary())

        except:
            st.error("❌ Tukey test failed")

    # ---------------- Plot ---------------- #
    if st.button("Show Boxplot"):
        try:
            if len(factors) == 0:
                st.warning("Select at least one factor")
            else:
                factor = factors[0]

                plt.figure(figsize=(8,5))
                df.boxplot(column=target, by=factor)
                plt.title("Boxplot")
                plt.suptitle("")
                st.pyplot(plt)

        except:
            st.error("❌ Plot error")