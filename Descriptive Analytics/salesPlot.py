import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv("train_cleansed.csv")

def sales_plot_by_group(group, top=50, color='blue'):
    sales_by_group = df.groupby(group)['Sales'].sum().sort_values(ascending=False).head(top)
    plt.figure(figsize=(15,4)) 
    plt.title(f'Sales by {group}')
    plt.ylabel('Sales in USD')
    bars = plt.bar(sales_by_group.index, sales_by_group.values, color=color, alpha=0.5)
    plt.xticks(rotation=90)
    # Add total sales to each bar, numbers displayed horizontally
    for i, (cls, sales) in enumerate(sales_by_group.items()):
        plt.text(i, sales/2, f'${int(sales):,}', ha='center', va='center', fontsize=12)
    plt.tight_layout()
    plt.show()

sales_plot_by_group('State', 10, color='blue')
sales_plot_by_group('Region', color='red')
sales_plot_by_group('Category', color='gray')
sales_plot_by_group('Sub-Category', color='green')
sales_plot_by_group('Segment', color='orange')
sales_plot_by_group('Ship Mode', color='brown')
sales_plot_by_group('Product Name', 10, color='blue')
sales_plot_by_group('Customer Name', 10, color='red')
