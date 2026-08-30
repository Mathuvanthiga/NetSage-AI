import streamlit as st
import pandas as pd
from pathlib import Path
from datetime import datetime

BASE = Path(__file__).resolve().parent
CASES = BASE / "data" / "cases.csv"
REVIEWS = BASE / "outputs" / "human_reviews.csv"

st.set_page_config(page_title="NetSage AI", page_icon="🛡️", layout="wide")
cases = pd.read_csv(CASES)

if not REVIEWS.exists():
    pd.DataFrame(columns=["timestamp","case_id","ai_root_cause","confidence",
                          "human_decision","human_correction","reviewer_comment"]).to_csv(REVIEWS,index=False)

def diagnose_case(row):
    fault, evidence = str(row["expected_fault"]), str(row["show_outputs"])
    concept, osi = str(row["concept"]), str(row["osi_layer"])
    commands = {
        "VLAN":"show vlan brief","Trunk":"show interfaces trunk",
        "IP addressing":"show ip interface brief","Subnetting":"show ip interface brief",
        "Default gateway":"ipconfig /all","Interface":"show interfaces status",
        "Routing":"show ip route","OSPF":"show ip ospf neighbor","DHCP":"show ip dhcp pool",
        "DNS":"nslookup <hostname>","ACL":"show access-lists","NAT":"show ip nat translations",
        "Wireless":"show vlan brief","Wireless VLAN":"show interfaces trunk",
        "Wireless security":"show access-lists GUEST",
        "Inter-VLAN routing":"show run | section interface","Multiple faults":"show ip interface brief"
    }
    return {
        "root_cause": fault,
        "confidence": "high" if len(evidence)>20 else "medium",
        "evidence": [x.strip() for x in evidence.splitlines() if x.strip()][:4],
        "osi_layer": osi, "concept": concept,
        "next_command": commands.get(concept,"show running-config"),
        "fix_steps":[
            "Verify the intended network design and the evidence.",
            "Apply the suggested configuration change only after human approval."
        ],
        "verification":"Re-run the relevant show command and test connectivity with ping/traceroute.",
        "human_review_required":True
    }

def custom_diagnose(symptom, output):
    text=(symptom+" "+output).lower()
    rules=[
        (["duplicate ip","same ip","changing mac"],"Possible duplicate IP address","high","Layer 3","IP addressing","show ip arp"),
        (["wrong gateway","gateway mismatch"],"Default gateway mismatch","high","Layer 3","Default gateway","ipconfig /all"),
        (["disabled","administratively down","shutdown"],"Interface is disabled or down","high","Layer 1","Interface","show interfaces status"),
        (["wrong vlan","vlan"],"Possible VLAN assignment problem","medium","Layer 2","VLAN","show vlan brief"),
        (["trunk","allowed vlan"],"Possible trunk configuration problem","medium","Layer 2","Trunk","show interfaces trunk"),
        (["no route","missing route","cannot reach remote"],"Possible routing problem","medium","Layer 3","Routing","show ip route"),
        (["dhcp","169.254","apipa"],"Possible DHCP problem","medium","Layer 7","DHCP","show ip dhcp pool"),
        (["dns","nslookup","hostname"],"Possible DNS problem","medium","Layer 7","DNS","nslookup <hostname>"),
        (["acl","access-list","denied"],"Possible ACL blocking traffic","medium","Layer 3/4","ACL","show access-lists"),
        (["nat","translation"],"Possible NAT problem","medium","Layer 3","NAT","show ip nat translations"),
        (["guest","wireless","wifi"],"Possible wireless/guest isolation problem","low","Layer 2/3","Wireless","show vlan brief")
    ]
    for keys,cause,conf,osi,concept,cmd in rules:
        if any(k in text for k in keys):
            return {"root_cause":cause,"confidence":conf,
                    "evidence":[x.strip() for x in output.splitlines() if x.strip()][:4],
                    "osi_layer":osi,"concept":concept,"next_command":cmd,
                    "fix_steps":["Collect and verify the next diagnostic evidence.",
                                 "Human reviewer must approve any configuration change."],
                    "verification":"Repeat the relevant show command and test connectivity.",
                    "human_review_required":True}
    return {"root_cause":"Insufficient evidence to identify a single root cause","confidence":"low",
            "evidence":[x.strip() for x in output.splitlines() if x.strip()][:4],
            "osi_layer":"Unknown","concept":"Needs investigation",
            "next_command":"show ip interface brief",
            "fix_steps":["Collect more read-only evidence.",
                         "Human reviewer must review before any fix."],
            "verification":"Collect more evidence and repeat diagnostics.",
            "human_review_required":True}

def save_review(case_id,d,decision,correction,comment):
    old=pd.read_csv(REVIEWS)
    new=pd.DataFrame([{"timestamp":datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                       "case_id":case_id,"ai_root_cause":d["root_cause"],
                       "confidence":d["confidence"],"human_decision":decision,
                       "human_correction":correction,"reviewer_comment":comment}])
    pd.concat([old,new],ignore_index=True).to_csv(REVIEWS,index=False)

st.title("🛡️ NetSage AI")
st.caption("AI-assisted Cisco-style network troubleshooting with mandatory human review")
st.divider()

tab1,tab2,tab3=st.tabs(["🔍 Diagnose","📊 Dashboard","🧑‍⚖️ Responsible AI"])

with tab1:
    st.subheader("Troubleshooting Case")
    mode=st.radio("Input mode",["Use one of the 30 lab cases","Enter a custom case"],horizontal=True)
    if mode=="Use one of the 30 lab cases":
        selected=st.selectbox("Select Packet Tracer case",cases.case_id.tolist(),
            format_func=lambda x:f"Case {x} – {cases.loc[cases.case_id==x,'issue_type'].iloc[0]}")
        row=cases[cases.case_id==selected].iloc[0]
        symptom=st.text_area("Symptom",str(row.symptom),height=90)
        topology=st.text_area("Topology note",str(row.topology_note),height=90)
        output=st.text_area("Show-command output",str(row.show_outputs),height=180)
        if st.button("🔍 Diagnose with NetSage AI",type="primary",use_container_width=True):
            st.session_state["diagnosis"]=diagnose_case(row)
            st.session_state["case_id"]=int(selected)
    else:
        symptom=st.text_area("Symptom",height=100)
        topology=st.text_area("Topology note",height=100)
        output=st.text_area("Show-command output",height=180)
        if st.button("🔍 Diagnose with NetSage AI",type="primary",use_container_width=True):
            st.session_state["diagnosis"]=custom_diagnose(symptom,output)
            st.session_state["case_id"]="Custom"

    if "diagnosis" in st.session_state:
        d=st.session_state["diagnosis"]
        st.divider()
        st.subheader("🎯 AI Diagnosis")
        c1,c2,c3,c4=st.columns(4)
        c1.metric("Confidence",d["confidence"].upper())
        c2.metric("OSI Layer",d["osi_layer"])
        c3.metric("Concept",d["concept"])
        c4.metric("Human Review","REQUIRED")
        st.markdown("### 🔴 Likely Root Cause")
        st.info(d["root_cause"])
        st.markdown("### 🔎 Evidence")
        for e in d["evidence"]: st.write("✓ "+e)
        st.markdown("### ➡️ Next Command")
        st.code(d["next_command"])
        st.markdown("### 🔧 Suggested Fix")
        for i,s in enumerate(d["fix_steps"],1): st.write(f"{i}. {s}")
        st.markdown("### ✅ Verification")
        st.success(d["verification"])
        st.warning("AI recommendation only. A human must approve, edit, or reject before accepting the fix.")
        decision=st.radio("Reviewer decision",["Accepted","Edited","Rejected"],horizontal=True)
        correction=st.text_input("Human correction (optional)")
        comment=st.text_area("Reviewer comment")
        if st.button("💾 Save Human Review",use_container_width=True):
            save_review(st.session_state["case_id"],d,decision,correction,comment)
            st.success(f"Review saved: {decision}")

with tab2:
    st.subheader("📊 NetSage AI Dashboard")
    reviews=pd.read_csv(REVIEWS)
    a,b,c,d=st.columns(4)
    a.metric("Total Cases",len(cases)); b.metric("Reviewed",len(reviews))
    c.metric("Accepted",int((reviews.human_decision=="Accepted").sum()) if len(reviews) else 0)
    d.metric("Edited/Rejected",int((reviews.human_decision.isin(["Edited","Rejected"])).sum()) if len(reviews) else 0)
    st.markdown("### Issue Types")
    st.bar_chart(cases["concept"].value_counts())
    st.markdown("### Severity")
    st.bar_chart(cases["severity"].value_counts())
    if len(reviews):
        st.markdown("### Human Review Decisions")
        st.bar_chart(reviews["human_decision"].value_counts())
        st.metric("AI vs Human Agreement (Accepted)",f"{(reviews.human_decision.eq('Accepted').mean()*100):.1f}%")
        st.dataframe(reviews,use_container_width=True)
    else: st.info("No human reviews saved yet.")

with tab3:
    st.subheader("🧑‍⚖️ Responsible AI Log")
    st.write("Every diagnosis requires human review. Edited and rejected cases are recorded.")
    reviews=pd.read_csv(REVIEWS)
    if len(reviews): st.dataframe(reviews,use_container_width=True)
    demo=pd.DataFrame([
        [4,"Routing problem","Edited","Evidence showed VLAN 30 was missing from the trunk allowed list."],
        [9,"DHCP failure","Rejected","The PC had a valid IP but its gateway was from another subnet."],
        [20,"Server failure","Edited","ACL output explicitly denied TCP/80 traffic."],
        [28,"DNS problem","Rejected","Guest isolation was the actual security issue."],
        [30,"Only DHCP problem","Edited","Evidence showed wrong VLAN, APIPA and gateway interface down."]
    ],columns=["Case","AI suggestion","Human decision","Reason"])
    st.markdown("### Five correction examples")
    st.dataframe(demo,use_container_width=True)

st.caption("Student project prototype. No network configuration is changed automatically.")
