"""Chat API endpoint — mock responses until LLM pipeline is built."""
from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional
import uuid

router = APIRouter(prefix="/api", tags=["chat"])


class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None
    language: str = "en"
    private_mode: bool = True


class ChatResponse(BaseModel):
    response: str
    plain_language: Optional[str] = None
    professional: Optional[str] = None
    legal: Optional[str] = None
    confidence: str = "high"
    sources: list[str] = []
    source_urls: list[str] = []
    session_id: str


MOCK_RESPONSES: dict[tuple[str, ...], dict] = {
    ("iso 27001", "iso27001", "isms", "information security management"): {
        "response": "ISO 27001 is the international standard for Information Security Management Systems (ISMS). It provides a systematic approach to managing sensitive company information so that it remains secure. It covers people, processes, and technology.\n\nOrganizations that achieve ISO 27001 certification demonstrate they have implemented comprehensive controls to protect data confidentiality, integrity, and availability.",
        "plain_language": "ISO 27001 is a rulebook for keeping company data safe. It helps you set up rules, train your team, and put locks on digital information. Companies that follow it earn a trusted certificate.",
        "professional": "ISO 27001 establishes requirements for an Information Security Management System (ISMS). Organizations must conduct risk assessments, implement controls from Annex A, and undergo periodic audits. Certification demonstrates systematic security governance to stakeholders and clients.",
        "legal": "ISO/IEC 27001:2022 Clause 4.1: The organization shall determine external and internal issues relevant to its purpose and its ability to achieve the intended outcome(s) of its information security management system.\n\nClause 6.1.2: The organization shall define and apply an information security risk assessment process that identifies risks, analyzes risks, and evaluates risks.\n\nAnnex A provides 93 controls across 4 themes: Organizational (37), People (8), Physical (14), and Technological (34).\n\nClause 9.2: Internal audits shall be conducted at planned intervals to provide information on whether the ISMS conforms to the organization's own requirements and the requirements of this standard.\n\nClause 10.1: The organization shall react to nonconformities and take action to control and correct them.",
        "confidence": "high",
        "sources": ["ISO/IEC 27001:2022 — Information Security Management Systems", "NIST CSF 2.0 — Framework Comparison"],
        "source_urls": ["https://www.iso.org/standard/27001", "https://www.nist.gov/cyberframework"],
    },
    ("breach notification", "breach", "notify", "notification", "data breach", "report breach"): {
        "response": "Under Nepal's Electronic Transactions Act 2063 (2006), unauthorized access to computer systems is punishable by up to 3 years imprisonment or NPR 30,000 fine. The proposed Digital Privacy and Data Protection Act (pending as of 2025) would introduce mandatory 48-hour breach notification.\n\nCurrently, there is no explicit breach notification timeline in existing Nepali law, but the Cyber Security Bylaw 2077 requires Telecom Service Providers to report security incidents to the NTA.",
        "plain_language": "Nepal doesn't yet have a strict rule about how fast you must report a data breach. But if you're an ISP or telecom company, you must tell the NTA about security problems. A new law being made may require reporting within 48 hours.",
        "professional": "Nepal's regulatory framework currently lacks a universal breach notification mandate. The ETA 2063 criminalizes unauthorized access with penalties up to 3 years imprisonment. The Cyber Security Bylaw 2077 requires TSPs to report incidents to NTA. The pending Digital Privacy and Data Protection Act proposes a 48-hour notification window for all organizations.",
        "legal": "Electronic Transactions Act 2063, Section 47: Any person who accesses or causes to be accessed any computer, computer system or computer network without authorization shall be punished with imprisonment up to 3 years or fine up to NPR 30,000 or both.\n\nCyber Security Bylaw 2077, Section 8: Every telecom service provider shall report any security incident to the Authority within twenty-four hours of becoming aware of such incident.\n\nProposed Digital Privacy and Data Protection Act (2025 Draft), Section 23: A data fiduciary shall notify the Authority of any personal data breach within forty-eight hours of becoming aware of such breach.\n\nSection 24: The notification shall include the nature of the breach, the categories and approximate number of data principals affected, and the measures taken or proposed to be taken.\n\nSection 25: Where the breach is likely to result in a high risk to the rights and freedoms of data principals, the data fiduciary shall also communicate the breach to the affected data principals.",
        "confidence": "medium",
        "sources": ["Electronic Transactions Act 2063 — Section 47", "Cyber Security Bylaw 2077 — Section 8", "Proposed Digital Privacy and Data Protection Act (2025 draft) — Sections 23-25"],
        "source_urls": ["https://www.ita.gov.np/", "https://www.nta.gov.np/", "https://moict.gov.np/"],
    },
    ("data protection", "privacy", "personal data", "collect data", "data collection", "individual privacy"): {
        "response": "Nepal's Individual Privacy Act 2075 (2018) protects personal data of individuals. It establishes principles for data collection, processing, and storage. The Data Act 2079 (2022) adds further data governance provisions.\n\nKey requirements include obtaining consent before collecting personal data, using data only for its stated purpose, and ensuring adequate security measures.",
        "plain_language": "Nepal has a privacy law that says companies must ask before collecting your personal info, can only use it for what they said they would, and must keep it safe. If they break these rules, they can face legal consequences.",
        "professional": "The Individual Privacy Act 2075 establishes data protection principles including purpose limitation, consent requirements, and security obligations. Organizations processing personal data of Nepal residents must implement appropriate technical and organizational measures. The Data Act 2079 supplements these requirements with additional data governance provisions.",
        "legal": "Individual Privacy Act 2075, Section 5: No person shall collect, process, or use personal information of any individual without prior consent of such individual, except as provided by this Act.\n\nSection 6: Personal information shall be collected only for a specific and lawful purpose and shall not be processed in a manner incompatible with that purpose.\n\nSection 7: The data controller shall ensure that personal information is accurate, complete, and up to date.\n\nSection 8: Personal information shall be retained only for as long as necessary to fulfill the purpose for which it was collected.\n\nSection 9: The data controller shall implement appropriate security measures to protect personal information from unauthorized access, disclosure, alteration, or destruction.\n\nSection 10: Every individual has the right to access their personal information held by a data controller.\n\nSection 11: Every individual has the right to request correction or deletion of their personal information.\n\nSection 12: Any person who contravenes the provisions of this Act shall be liable for penalties as prescribed.",
        "confidence": "high",
        "sources": ["Individual Privacy Act 2075 (2018) — Sections 5-12", "Data Act 2079 (2022) — Data Governance Provisions"],
        "source_urls": ["https://www.lawcommission.gov.np/", "https://moict.gov.np/"],
    },
    ("nist csf", "nist", "cybersecurity framework", "cyber security framework"): {
        "response": "The NIST Cybersecurity Framework 2.0 is a voluntary framework that helps organizations manage cybersecurity risk. It has 6 core functions: Govern, Identify, Protect, Detect, Respond, and Recover.\n\nIt's widely used globally and maps to ISO 27001 controls. For startups in Nepal, it provides a practical roadmap for building security maturity.",
        "plain_language": "NIST CSF is a free to-do list for cybersecurity. It has 6 main areas: make rules, know your risks, protect your stuff, spot problems, fix problems, and recover. It's used by companies worldwide.",
        "professional": "NIST CSF 2.0 provides a risk-based approach to cybersecurity through six core functions: Govern (GV), Identify (ID), Protect (PR), Detect (DE), Respond (RS), and Recover (RC). Each function contains categories and subcategories that map to specific outcomes. The framework is adaptable to organizations of any size or sector.",
        "legal": "NIST Cybersecurity Framework 2.0 (February 2024), Section 1: The Framework is voluntary and provides standards, guidelines, and best practices for managing cybersecurity-related risk.\n\nGovern (GV): The organization's cybersecurity risk management strategy, expectations, and policy are established, communicated, and monitored.\n\nIdentify (ID): The organization understands its cybersecurity risks to systems, assets, data, and capabilities.\n\nProtect (PR): The organization safeguards its services by implementing appropriate safeguards.\n\nDetect (DE): The organization identifies cybersecurity events in a timely manner.\n\nRespond (RS): The organization takes action regarding a detected cybersecurity incident.\n\nRecover (RC): The organization maintains plans for resilience and restores capabilities or services impaired by cybersecurity incidents.\n\nSection 2: The Framework Implementation Tiers (Partial, Risk-Informed, Repeatable, Adaptive) describe the degree to which an organization's cybersecurity risk management practices exhibit characteristics defined in the Framework.",
        "confidence": "high",
        "sources": ["NIST Cybersecurity Framework 2.0 — February 2024", "ISO 27001 Cross-Reference Mapping"],
        "source_urls": ["https://www.nist.gov/cyberframework", "https://doi.org/10.6028/NIST.CSWP.29"],
    },
    ("penalty", "penalties", "fine", "imprisonment", "jail", "punishment", "punish", "offense", "offence", "crime", "criminal", "eta 2063", "electronic transactions"): {
        "response": "Penalties under Nepal's Electronic Transactions Act 2063 vary by offense:\n\n• Unauthorized access: Up to 3 years imprisonment or NPR 30,000 fine (or both)\n• Data alteration: Up to 5 years imprisonment or NPR 50,000 fine\n• Privacy breach: Up to 3 years imprisonment or NPR 30,000 fine\n• Publishing false information: Up to 2 years imprisonment or NPR 20,000 fine",
        "plain_language": "If someone hacks into a system in Nepal, they can go to jail for up to 3 years or pay Rs 30,000. Changing data illegally can get you 5 years in jail. Sharing fake information online can get you 2 years.",
        "professional": "The Electronic Transactions Act 2063 prescribes graduated penalties for cyber offenses. Unauthorized access carries up to 3 years imprisonment or NPR 30,000 fine. Data tampering carries up to 5 years or NPR 50,000. Privacy violations carry up to 3 years or NPR 30,000. Organizations should implement access controls and monitoring to mitigate these risks.",
        "legal": "Electronic Transactions Act 2063:\n\nSection 47(1): Unauthorized access — Any person who accesses or causes to be accessed any computer, computer system or computer network without authorization shall be punished with imprisonment up to 3 years or fine up to NPR 30,000 or both.\n\nSection 47(2): Data alteration — Any person who dishonestly or fraudulently alters, destroys, deletes, or renders ineffective any data contained in a computer shall be punished with imprisonment up to 5 years or fine up to NPR 50,000 or both.\n\nSection 48: Privacy breach — Any person who obtains, discloses, or sells personal information of another person without authorization shall be punished with imprisonment up to 3 years or fine up to NPR 30,000 or both.\n\nSection 49: Publishing false information — Any person who publishes or causes to be published any information that is false or misleading in a computer system shall be punished with imprisonment up to 2 years or fine up to NPR 20,000 or both.\n\nSection 50: Attempt and abetment — Any person who attempts or abets the commission of any offense under this Act shall be punished with the same punishment as prescribed for the offense.\n\nCyber Security Bylaw 2077, Section 12: The Authority may impose additional administrative penalties including license suspension for repeated violations.",
        "confidence": "high",
        "sources": ["Electronic Transactions Act 2063 — Sections 47-50", "Cyber Security Bylaw 2077 — Section 12"],
        "source_urls": ["https://www.ita.gov.np/", "https://www.nta.gov.np/"],
    },
    ("gap assessment", "gap", "assessment", "compliance check", "compliance score", "evaluate"): {
        "response": "I can help you start a compliance gap assessment! This will evaluate your organization's current security posture against Nepal's regulatory requirements and international standards.\n\nThe assessment covers 5 key domains:\n1. Incident Response\n2. Data Protection\n3. Access Controls\n4. Security Awareness Training\n5. Third-Party Risk\n\nWould you like to begin? It takes approximately 10-15 minutes.",
        "plain_language": "I'll ask you simple yes/no questions about your company's security. It takes about 10 minutes and gives you a score showing where you need to improve. It's like a health check for your company's data safety.",
        "professional": "The gap assessment evaluates your organization's compliance posture across 5 domains aligned with Nepal's regulatory framework and ISO 27001/NIST CSF standards. Results include a scored report with prioritized remediation steps and a timeline for achieving compliance.",
        "legal": "Assessment domains are derived from: Nepal Cyber Security Policy 2023 (Strategic Objectives 3-7), ISO 27001:2022 Annex A Controls, NIST CSF 2.0 Categories.\n\nDomain 1 — Incident Response: Aligned with National Cyber Security Policy 2023, Strategic Objective 4 and NIST CSF RS function.\n\nDomain 2 — Data Protection: Aligned with Individual Privacy Act 2075 Sections 5-12 and ISO 27001 Annex A.8.\n\nDomain 3 — Access Controls: Aligned with ISO 27001 Annex A.9 and NIST CSF PR.AC category.\n\nDomain 4 — Security Awareness Training: Aligned with ISO 27001 Annex A.6.3 and NIST CSF PR.AT category.\n\nDomain 5 — Third-Party Risk: Aligned with ISO 27001 Annex A.5.19-5.23 and NIST CSF ID.SC category.\n\nThe assessment produces a compliance score per domain and an overall maturity rating on a 5-point scale.",
        "confidence": "high",
        "sources": ["Nepal Cyber Security Policy 2023", "ISO 27001:2022 Annex A", "NIST CSF 2.0"],
        "source_urls": ["https://www.iso.org/standard/27001", "https://www.nist.gov/cyberframework"],
    },
    ("incident response", "incident", "security incident", "breach response"): {
        "response": "Incident response is how your organization detects, contains, and recovers from security incidents. Nepal's Cyber Security Policy 2023 requires organizations to establish incident response teams.\n\nA good incident response plan has 6 phases: Preparation, Identification, Containment, Eradication, Recovery, and Lessons Learned.",
        "plain_language": "When something bad happens to your company's computers, you need a plan to fix it fast. Nepal's law says you must have a team ready. The plan has 6 steps: get ready, find the problem, stop it, remove it, fix everything, and learn from it.",
        "professional": "Incident response is a structured approach to managing security breaches. Nepal's Cyber Security Policy 2023 mandates incident response capabilities. Organizations should implement NIST SP 800-61 aligned procedures covering preparation, detection, containment, eradication, recovery, and post-incident analysis.",
        "legal": "National Cyber Security Policy 2023, Strategic Objective 4: Establish mechanisms for incident response and recovery across critical information infrastructure.\n\nNIST SP 800-61 Rev. 2: Computer Security Incident Handling Guide — defines four phases: Preparation, Detection & Analysis, Containment/Eradication/Recovery, and Post-Incident Activity.\n\nISO 27001:2022 Annex A.5.24: The organization shall plan and prepare for managing information security incidents by defining, establishing, and communicating an information security incident management process.\n\nAnnex A.5.25: The organization shall assess information security events and decide if they are to be classified as information security incidents.\n\nAnnex A.5.26: The organization shall respond to information security incidents in a timely manner.\n\nAnnex A.5.27: The organization shall learn from information security incidents to improve the incident management process.\n\nCyber Security Bylaw 2077, Section 8: Every telecom service provider shall report any security incident to the Authority within twenty-four hours.",
        "confidence": "high",
        "sources": ["National Cyber Security Policy 2023 — Strategic Objective 4", "NIST SP 800-61", "ISO 27001:2022 — Annex A.5.24-5.27"],
        "source_urls": ["https://www.nist.gov/publications/computer-security-incident-handling-guide", "https://www.iso.org/standard/27001"],
    },
    ("access control", "access", "password", "authentication", "authorization", "role-based"): {
        "response": "Access control ensures only authorized people can view or use specific data and systems. It's a core requirement under both ISO 27001 (Annex A.9) and Nepal's cyber security policies.\n\nKey practices include: least privilege principle, multi-factor authentication, regular access reviews, and role-based access control (RBAC).",
        "plain_language": "Only the right people should see company data. Use strong passwords, give people access only to what they need, and check regularly who has access to what. This prevents data leaks.",
        "professional": "Access control is a fundamental security mechanism. ISO 27001 Annex A.9 mandates systematic access control including user registration, privilege management, authentication mechanisms, and regular access rights review. Organizations should implement least privilege and RBAC principles.",
        "legal": "ISO 27001:2022 Annex A.9.1: Access control policy — The organization shall develop, implement, and maintain an access control policy appropriate to the business requirements.\n\nAnnex A.9.2: User access management — The organization shall implement a user registration and de-registration process and a user access provisioning process.\n\nAnnex A.9.3: User responsibilities — Users shall follow the organization's practices in the use of secret authentication information.\n\nAnnex A.9.4: System and application access control — Information access restricted in accordance with the access control policy.\n\nNational Cyber Security Policy 2023, Section 3.4: All organizations shall implement multi-factor authentication for critical systems and role-based access control for all information assets.\n\nIndividual Privacy Act 2075, Section 9: The data controller shall implement appropriate security measures to protect personal information from unauthorized access.",
        "confidence": "high",
        "sources": ["ISO 27001:2022 — Annex A.9 Access Control", "National Cyber Security Policy 2023 — Section 3.4"],
        "source_urls": ["https://www.iso.org/standard/27001", "https://moict.gov.np/"],
    },
    ("cyber security bylaw", "bylaw", "bylaws", "nta", "telecom", "isp"): {
        "response": "The Cyber Security Bylaw 2077 (2020) is mandatory for all Telecom Service Providers and ISPs in Nepal. It's monitored by the Nepal Telecommunications Authority (NTA).\n\nKey requirements include: quarterly IS audits, 24/7 security monitoring, incident response teams, and annual security reports to the NTA.",
        "plain_language": "If you're an internet or phone company in Nepal, you must follow strict security rules. You need to do security checks every 3 months, watch for problems 24/7, and report to the NTA every year.",
        "professional": "The Cyber Security Bylaw 2077 mandates TSPs/ISPs to implement continuous security monitoring, quarterly audits, incident response capabilities, and regulatory reporting to NTA. Non-compliance can result in license suspension or financial penalties.",
        "legal": "Cyber Security Bylaw 2077:\n\nSection 3: Every telecom service provider shall establish and maintain a comprehensive information security management system.\n\nSection 5: Every telecom service provider shall establish a 24x7 security operations center and conduct quarterly information security audits.\n\nSection 6: The security operations center shall monitor, detect, and respond to security incidents in real-time.\n\nSection 7: Every telecom service provider shall designate a Chief Information Security Officer responsible for compliance with this Bylaw.\n\nSection 8: Every telecom service provider shall report any security incident to the Authority within twenty-four hours of becoming aware of such incident.\n\nSection 9: The Authority may conduct inspections and audits to ensure compliance.\n\nSection 12: The Authority may impose administrative penalties including fines up to NPR 5,000,000 or suspension of license for repeated violations.\n\nSection 15: Every telecom service provider shall submit an annual security report to the Authority by the end of each fiscal year.",
        "confidence": "high",
        "sources": ["Cyber Security Bylaw 2077 (2020) — NTA Mandatory Requirements"],
        "source_urls": ["https://www.nta.gov.np/", "https://www.nta.gov.np/uploads/regulations/Cyber_Security_Bylaw_2077.pdf"],
    },
}

DEFAULT_RESPONSE = {
    "response": "That's a great question! Based on Nepal's regulatory framework, I can help you understand compliance requirements.\n\nFor specific details about your query, I recommend consulting the official policy documents. The key regulations governing this area include the Electronic Transactions Act 2063, the Cyber Security Bylaw 2077, and the Individual Privacy Act 2075.\n\nWould you like me to explain any of these in more detail?",
    "plain_language": "I'm not sure about that exact question yet. But I know about Nepal's main tech laws — the Electronic Transactions Act, the Cyber Security Bylaw, and the Privacy Act. Want me to tell you about any of them?",
    "professional": "Your query relates to Nepal's regulatory framework. Key applicable legislation includes the ETA 2063, Cyber Security Bylaw 2077, and Privacy Act 2075. I can provide detailed analysis of specific provisions upon request.",
    "legal": "Applicable regulatory instruments: Electronic Transactions Act 2063, Cyber Security Bylaw 2077, Individual Privacy Act 2075, Data Act 2079, National Cyber Security Policy 2023. Please specify the regulatory area for a detailed legal analysis.",
    "confidence": "medium",
    "sources": ["Electronic Transactions Act 2063", "Cyber Security Bylaw 2077", "Individual Privacy Act 2075"],
    "source_urls": ["https://www.ita.gov.np/", "https://www.nta.gov.np/"],
}

# Nepali translations
NEPALI_RESPONSES: dict[str, dict] = {
    "iso 27001": {
        "response": "ISO 27001 भनेको सूचना सुरक्षा व्यवस्थापन प्रणाली (ISMS) को लागि अन्तर्राष्ट्रिय मापदण्ड हो। यसले संवेदनशील कम्पनी जानकारीलाई सुरक्षित राख्न प्रणालीगत दृष्टिकोण प्रदान गर्दछ। यसले मानिसहरू, प्रक्रियाहरू, र प्रविधिलाई समेट्छ।",
        "plain_language": "ISO 27001 कम्पनीको डेटा सुरक्षित राख्ने नियमपुस्तक हो। यसले तपाईंलाई नियमहरू बनाउन, टोलीलाई तालिम दिन, र डिजिटल जानकारीमा ताला लगाउन मद्दत गर्दछ।",
        "professional": "ISO 27001 ले ISMS का लागि आवश्यकताहरू स्थापित गर्दछ। संस्थाहरूले जोखिम मूल्याङ्कन गर्नुपर्छ, Annex A बाट नियन्त्रणहरू कार्यान्वयन गर्नुपर्छ, र नियमित अडिट गर्नुपर्छ।",
        "legal": "ISO/IEC 27001:2022 खण्ड 4.1: संगठनले आफ्नो उद्देश्य र ISMS को अपेक्षित परिणामहरू प्राप्त गर्ने क्षमतासँग सम्बन्धित बाह्य र आन्तरिक मुद्दाहरू निर्धारण गर्नुपर्छ।",
    },
    "penalties": {
        "response": "नेपालको इलेक्ट्रोनिक लेनदेन ऐन २०६३ अन्तर्गत दण्डहरू:\n\n• अनधिकृत पहुँच: ३ वर्षसम्म कैद वा रु. ३०,००० जरिवाना\n• डेटा परिवर्तन: ५ वर्षसम्म कैद वा रु. ५०,००० जरिवाना\n• गोपनीयता उल्लंघन: ३ वर्षसम्म कैद वा रु. ३०,००० जरिवाना",
        "plain_language": "नेपालमा कसैले सिस्टम ह्याक गरे ३ वर्षसम्म कैद वा रु. ३०,००० जरिवाना लाग्न सक्छ। डेटा अवैध रूपमा परिवर्तन गरे ५ वर्षसम्म कैद हुन सक्छ।",
        "professional": "इलेक्ट्रोनिक लेनदेन ऐन २०६३ ले साइबर अपराधहरूको लागि क्रमिक दण्डहरू निर्धारण गर्दछ। अनधिकृत पहुँचको लागि ३ वर्षसम्म कैद वा रु. ३०,००० जरिवाना।",
        "legal": "इलेक्ट्रोनिक लेनदेन ऐन २०६३:\n\nखण्ड ४७(१): अनधिकृत पहुँच — कम्प्युटरमा अनधिकृत पहुँच गर्ने व्यक्तिलाई ३ वर्षसम्म कैद वा रु. ३०,००० जरिवाना वा दुवै।\n\nखण्ड ४७(२): डेटा परिवर्तन — डेटा परिवर्तन गर्ने व्यक्तिलाई ५ वर्षसम्म कैद वा रु. ५०,००० जरिवाना वा दुवै।\n\nखण्ड ४८: गोपनीयता उल्लंघन — व्यक्तिगत जानकारी अनधिकृत रूपमा प्राप्त वा प्रकट गर्ने व्यक्तिलाई ३ वर्षसम्म कैद वा रु. ३०,००० जरिवाना वा दुवै।",
    },
    "incident response": {
        "response": "घटना प्रतिक्रिया भनेको तपाईंको संस्थाले सुरक्षा घटनाहरू कसरी पत्ता लगाउँछ, नियन्त्रण गर्छ र पुनर्स्थापना गर्छ भन्ने हो। नेपालको साइबर सुरक्षा नीति २०२३ ले घटना प्रतिक्रिया टोली स्थापना गर्न आवश्यक गराउँछ।",
        "plain_language": "तपाईंको कम्पनीको कम्प्युटरमा केही खराब भएमा छिटो ठीक गर्ने योजना चाहिन्छ। नेपालको कानुनले तपाईंसँग तयार टोली हुनुपर्छ भन्छ।",
        "professional": "घटना प्रतिक्रिया सुरक्षा उल्लंघनहरू व्यवस्थापन गर्ने संरचित दृष्टिकोण हो। नेपालको साइबर सुरक्षा नीति २०२३ ले घटना प्रतिक्रिया क्षमता अनिवार्य गराउँछ।",
        "legal": "राष्ट्रिय साइबर सुरक्षा नीति २०२३, रणनीतिक उद्देश्य ४: महत्वपूर्ण सूचना पूर्वाधारमा घटना प्रतिक्रिया र पुनर्स्थापनाको लागि तन्त्र स्थापना गर्नुहोस्।\n\nNIST SP 800-61: कम्प्युटर सुरक्षा घटना ह्यान्डलिङ गाइड — चार चरणहरू: तयारी, पत्ता लगाउने र विश्लेषण, नियन्त्रण/उन्मूलन/पुनर्स्थापना, र घटनापछिको गतिविधि।",
    },
    "default": {
        "response": "त्यो राम्रो प्रश्न हो! नेपालको नियामक ढाँचाको आधारमा, म तपाईंलाई अनुपालन आवश्यकताहरू बुझ्न मद्दत गर्न सक्छु।\n\nतपाईंको प्रश्नको विशिष्ट विवरणको लागि, आधिकारिक नीति कागजातहरू परामर्श गर्नुहोस्।\n\nके तपाईं चाहनुहुन्छ म यी मध्ये कुनै बारेमा विस्तृत रूपमा बताउनु?",
        "plain_language": "म अझै त्यो विशिष्ट प्रश्नको बारेमा निश्चित छैन। तर म नेपालका मुख्य प्रविधि कानुनहरू जान्छु — इलेक्ट्रोनिक लेनदेन ऐन, साइबर सुरक्षा बाईला, र गोपनीयता ऐन।",
        "professional": "तपाईंको प्रश्न नेपालको नियामक ढाँचासँग सम्बन्धित छ। मुख्य कानुनहरू: इलेक्ट्रोनिक लेनदेन ऐन २०६३, साइबर सुरक्षा बाईला २०७७, र गोपनीयता ऐन २०७५।",
        "legal": "लागू नियामक उपकरणहरू: इलेक्ट्रोनिक लेनदेन ऐन २०६३, साइबर सुरक्षा बाईला २०७७, व्यक्तिगत गोपनीयता ऐन २०७५, डेटा ऐन २०७९। कृपया विस्तृत कानुनी विश्लेषणको लागि नियामक क्षेत्र निर्दिष्ट गर्नुहोस्।",
    },
}


def get_mock_response(message: str, language: str = "en") -> dict:
    msg_lower = message.lower()

    # Find matching response
    matched = None
    for keywords, response in MOCK_RESPONSES.items():
        for keyword in keywords:
            if keyword in msg_lower:
                matched = response
                break
        if matched:
            break

    if not matched:
        matched = DEFAULT_RESPONSE

    # If Nepali requested, overlay Nepali translations
    if language == "ne":
        # Find which topic matched
        ne_key = "default"
        for keyword_group in MOCK_RESPONSES.keys():
            for kw in keyword_group:
                if kw in msg_lower:
                    if any(k in keyword_group for k in ("iso 27001", "iso27001")):
                        ne_key = "iso 27001"
                    elif any(k in keyword_group for k in ("penalt", "fine", "imprisonment", "jail", "eta 2063")):
                        ne_key = "penalties"
                    elif any(k in keyword_group for k in ("incident", "breach response")):
                        ne_key = "incident response"
                    break
            if ne_key != "default":
                break

        ne = NEPALI_RESPONSES.get(ne_key, NEPALI_RESPONSES["default"])
        return {
            **matched,
            "response": ne["response"],
            "plain_language": ne["plain_language"],
            "professional": ne["professional"],
            "legal": ne["legal"],
        }

    return matched


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Process a chat message and return a response."""
    session_id = request.session_id or str(uuid.uuid4())
    mock = get_mock_response(request.message, request.language)

    return ChatResponse(
        response=mock["response"],
        plain_language=mock.get("plain_language"),
        professional=mock.get("professional"),
        legal=mock.get("legal"),
        confidence=mock["confidence"],
        sources=mock["sources"],
        source_urls=mock.get("source_urls", []),
        session_id=session_id,
    )
