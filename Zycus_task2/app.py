import streamlit as st

from task2_account_health import generate_account_health


st.set_page_config(
    page_title="Zycus Account Health",
    page_icon="📊",
    layout="centered",
)


st.title("Zycus Account Health")
st.write("Generate an account health brief for your QBR.")


account_id = st.text_input(
    "Account ID",
    placeholder="e.g. ACC-3336"
)


if st.button(
    "Generate Account Health",
    type="primary"
):

    if not account_id.strip():

        st.warning(
            "Please enter an account ID."
        )

    else:

        try:

            with st.spinner(
                "Generating account health brief..."
            ):

                result = generate_account_health(
                    account_id.strip()
                )

            st.subheader(
                "Executive Summary"
            )

            st.write(
                result.executive_summary
            )

            st.subheader(
                "Open Risks & Flagged Issues"
            )

            if result.open_risks_and_flagged_issues:

                for risk in (
                    result.open_risks_and_flagged_issues
                ):

                    st.markdown(
                        f"**{risk.issue}**"
                    )

                    st.write(
                        risk.reason
                    )

                    st.caption(
                        f"Ticket: {risk.ticket_id}"
                    )

                    st.info(
                        f'"{risk.direct_quote}"'
                    )

            else:

                st.success(
                    "No open risks or flagged issues identified."
                )

            st.subheader(
                "Recommended TAM Talking Points"
            )

            for point in (
                result.recommended_talking_points
            ):

                st.markdown(
                    f"- {point}"
                )

        except ValueError as error:

            st.error(
                str(error)
            )

        except Exception as error:

            st.error(
                f"Unable to generate account health: {error}"
            )