"""AI explanation layer for TaxLens AI."""

from __future__ import annotations

import json
import os


def get_api_key() -> str:
    """Load the API key from the environment or Streamlit secrets."""
    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    if api_key:
        return api_key

    try:
        import streamlit as st

        return str(st.secrets.get("OPENAI_API_KEY", "")).strip()
    except Exception:
        return ""


def built_in_explanation(inputs: dict, result: dict, side_gig: dict) -> str:
    """Always-available educational explanation when an API key is not configured."""
    balance = result["refund_or_amount_owed"]
    if balance >= 0:
        outlook = (
            f"You are currently projected to receive about ${balance:,.0f} back, "
            "assuming the information entered stays the same through year-end."
        )
    else:
        outlook = (
            f"You are currently projected to owe about ${abs(balance):,.0f}. "
            f"Spread across the remaining paychecks, that is roughly "
            f"${result['amount_per_remaining_paycheck']:,.0f} per paycheck."
        )

    points = [outlook]
    if result["side_gig_net_profit"] > 0:
        points.append(
            f"Your side gig produces approximately ${result['side_gig_net_profit']:,.0f} "
            f"of net profit. The model estimates about ${side_gig['incremental_tax']:,.0f} "
            f"of additional federal tax, or {side_gig['reserve_rate']:.0%} of net profit."
        )
    if inputs["projected_traditional_401k"] > 0:
        points.append(
            "The projected traditional 401(k) contribution reduces income used in this "
            "federal income-tax estimate."
        )
    points.append(
        "Treat this as an educational projection. Credits, itemized deductions, state "
        "taxes, health-insurance subsidies, and other personal facts can change the result."
    )
    return "\n\n".join(points)


def generate_ai_explanation(inputs: dict, result: dict, side_gig: dict) -> str:
    """Generate a concise coaching explanation with the OpenAI Responses API."""
    api_key = get_api_key()
    if not api_key:
        return built_in_explanation(inputs, result, side_gig)

    try:
        from openai import OpenAI

        client = OpenAI(api_key=api_key)
        model = os.getenv("OPENAI_MODEL", "gpt-5-mini")
        payload = {
            "inputs": inputs,
            "calculated_result": result,
            "side_gig_comparison": side_gig,
        }
        response = client.responses.create(
            model=model,
            instructions=(
                "You are the educational coach inside TaxLens AI. Explain only the "
                "provided Python calculations and never recalculate or invent values. "
                "The field refund_or_amount_owed has an important meaning: a positive "
                "value means a projected refund, while a negative value means the user "
                "is projected to owe money. The same sign rule applies to the Indiana "
                "state, county, and combined refund_or_amount_owed fields. Never describe "
                "a negative value as a refund. "
                "Use plain language for a student or recent graduate. Write four short "
                "sections: Outlook, Why, Next steps, and Limitations. Keep the entire "
                "response under 250 words. Do not use LaTeX or dollar signs because they "
                "cause formatting problems. Write amounts like 'USD 416.91' instead. "
                "Mention that this is an educational estimate and not tax advice."
            ),
            input=json.dumps(payload, indent=2),
        )
        return response.output_text
    except Exception:
        fallback = built_in_explanation(inputs, result, side_gig)
        return fallback


def generate_chat_response(
    messages: list[dict],
    inputs: dict,
    result: dict,
    side_gig: dict,
) -> str:
    """Answer a follow-up question using the current calculated projection."""
    api_key = get_api_key()
    if not api_key:
        return (
            "The interactive coach is unavailable right now, but the tax projection "
            "and built-in summary still work."
        )

    try:
        from openai import OpenAI

        client = OpenAI(api_key=api_key)
        model = os.getenv("OPENAI_MODEL", "gpt-5-mini")
        context = {
            "inputs": inputs,
            "calculated_result": result,
            "side_gig_comparison": side_gig,
        }
        conversation = [
            {
                "role": message["role"],
                "content": message["content"],
            }
            for message in messages[-12:]
            if message.get("role") in {"user", "assistant"}
        ]
        response = client.responses.create(
            model=model,
            instructions=(
                "You are the conversational tax coach inside TaxLens AI, an educational "
                "finance-class project for students and early-career workers. Use the "
                "current Python-calculated projection supplied in the first message. "
                "Do not alter, recalculate, or invent its numbers. A positive field ending "
                "in refund_or_amount_owed means a projected refund; a negative value means "
                "a projected amount owed. Answer the user's specific question directly in "
                "plain language, usually in 2 to 5 short paragraphs or bullets. You may "
                "explain tax concepts generally, but clearly say when something is outside "
                "the calculator's inputs. Never claim to file a return or give definitive "
                "personal tax advice. Do not use LaTeX or dollar signs; format money as "
                "'USD 416.91'."
            ),
            input=[
                {
                    "role": "user",
                    "content": (
                        "Here is the current calculator context. Treat it as authoritative:\n"
                        + json.dumps(context, indent=2)
                    ),
                },
                *conversation,
            ],
        )
        return response.output_text
    except Exception:
        return (
            "I couldn't reach the AI coach just now. Your calculated tax results are "
            "still available above, so please try your question again in a moment."
        )
