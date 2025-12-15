from aws_cdk import (
    aws_budgets as budgets,
)
from constructs import Construct

class BudgetConstruct(Construct):
    def __init__(self, scope: Construct, id: str, amount: float, email: str, **kwargs):
        super().__init__(scope, id, **kwargs)

        # OPTIMIZATION: Cost Alarm
        self.monthly_budget = budgets.CfnBudget(
            self, "MonthlyCostBudget",
            budget={
                "budgetType": "COST",
                "timeUnit": "MONTHLY",
                "budgetLimit": {
                    "amount": str(amount),
                    "unit": "USD"
                }
            },
            notifications_with_subscribers=[
                budgets.CfnBudget.NotificationWithSubscribersProperty(
                    notification=budgets.CfnBudget.NotificationProperty(
                        comparison_operator="GREATER_THAN",
                        notification_type="ACTUAL",
                        threshold=80, # Alert at 80% usage
                        threshold_type="PERCENTAGE"
                    ),
                    subscribers=[
                        budgets.CfnBudget.SubscriberProperty(
                            address=email,
                            subscription_type="EMAIL"
                        )
                    ]
                )
            ]
        )