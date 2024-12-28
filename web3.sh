#!/bin/bash
echo "Lancio IFinance"
source /home/developer/finance_venv/bin/activate
streamlit run /home/developer/PycharmProjects/learningProjects/IFinance/webMain.py --server.port=8503
