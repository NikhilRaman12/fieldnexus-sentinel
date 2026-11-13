import React, { useState } from 'react';

// Design tokens: Deep forest green (#1A3A2A), warm ivory (#F7F9F6), earthy accent (#8D6E63), muted gold (#D4AF37)
export const App: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'decision' | 'crop_guard' | 'market_sense' | 'input_trust' | 'governance'>('decision');
  const [loading, setLoading] = useState<boolean>(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  
  const [crop, setCrop] = useState<string>('Tomato');
  const [district, setDistrict] = useState<string>('Rangareddy');
  const [query, setQuery] = useState<string>('Yellowing lower foliage with dark concentric circular spots');
  const [quantity, setQuantity] = useState<number>(40);
  const [decisionResult, setDecisionResult] = useState<any>(null);

  const runDecisionCenter = async () => {
    if (quantity <= 0) {
      setErrorMsg('Harvest quantity must be greater than zero quintals.');
      return;
    }
    setErrorMsg(null);
    setLoading(true);

    try {
      const res = await fetch('/api/v1/decisions/plan', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          session_id: `session-${Date.now()}`,
          farmer_id: 'telangana-fpo-01',
          crop: crop,
          variety: 'Saaho 3251',
          district: district,
          latitude: 17.3850,
          longitude: 78.4867,
          crop_stage: 'flowering',
          farmer_query: query,
          symptom_location: 'lower_leaf',
          harvest_quantity_quintals: quantity,
          soil_ph: 6.8,
          has_soil_test: true,
          preferred_language: 'en'
        })
      });

      if (res.ok) {
        const data = await res.json();
        setDecisionResult(data);
      } else {
        const errData = await res.json().catch(() => ({}));
        setErrorMsg(errData.detail || `Service Error: Backend API returned HTTP ${res.status}.`);
        setDecisionResult(null);
      }
    } catch (e: any) {
      console.error(e);
      // HARDENING RULE: Never fabricate fake COMPLETED state or fake pesticide dosages when backend is unavailable
      setErrorMsg('Backend service unavailable (Connection Refused). Please ensure FastAPI backend is running at http://localhost:8000.');
      setDecisionResult(null);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column' }}>
      {/* Top Header */}
      <header style={{ backgroundColor: '#1A3A2A', color: '#F7F9F6', padding: '16px 32px', display: 'flex', justifyContent: 'space-between', alignItems: 'center', boxShadow: '0 2px 8px rgba(0,0,0,0.1)' }}>
        <div>
          <div style={{ fontSize: '24px', fontWeight: '700', letterSpacing: '0.5px' }}>
            KRISHIVA <span style={{ color: '#D4AF37' }}>AI</span>
          </div>
          <div style={{ fontSize: '12px', opacity: 0.85 }}>Farm-to-Market Agricultural Decision Intelligence (Buildathon Edition)</div>
        </div>
        <div style={{ display: 'flex', gap: '12px', alignItems: 'center' }}>
          <span style={{ fontSize: '12px', backgroundColor: 'rgba(255,255,255,0.1)', padding: '5px 12px', borderRadius: '16px' }}>
            📍 Pilot: Telangana (Tomato Only)
          </span>
          <span style={{ fontSize: '12px', backgroundColor: '#37474F', color: '#FFF', padding: '5px 12px', borderRadius: '16px' }}>
            DEMO / PROTOTYPE
          </span>
        </div>
      </header>

      {/* Navigation Bar */}
      <nav style={{ backgroundColor: '#FFFFFF', borderBottom: '1px solid #E0E6ED', padding: '0 32px', display: 'flex', gap: '24px' }}>
        {[
          { key: 'decision', label: '🌾 Farm Decision Center' },
          { key: 'crop_guard', label: '🛡️ Crop Guard (Tomato)' },
          { key: 'market_sense', label: '📈 Market Sense' },
          { key: 'input_trust', label: '🔬 Input Trust (Safety First)' },
          { key: 'governance', label: '⚖️ Provenance & ML Governance' },
        ].map((tab) => (
          <button
            key={tab.key}
            onClick={() => setActiveTab(tab.key as any)}
            style={{
              padding: '16px 0',
              border: 'none',
              background: 'none',
              cursor: 'pointer',
              fontWeight: activeTab === tab.key ? '700' : '500',
              color: activeTab === tab.key ? '#1A3A2A' : '#5A6B5C',
              borderBottom: activeTab === tab.key ? '3px solid #1A3A2A' : '3px solid transparent',
              fontSize: '14px'
            }}
          >
            {tab.label}
          </button>
        ))}
      </nav>

      {/* Main Container */}
      <main style={{ flex: 1, padding: '32px', maxWidth: '1280px', margin: '0 auto', width: '100%', boxSizing: 'border-box' }}>
        {errorMsg && (
          <div style={{ backgroundColor: '#FFEBEE', border: '1px solid #EF9A9A', color: '#C62828', padding: '14px 18px', borderRadius: '6px', marginBottom: '24px', fontSize: '14px' }}>
            ⚠️ <strong>Error Notice:</strong> {errorMsg}
          </div>
        )}

        {activeTab === 'decision' && (
          <div>
            <div style={{ marginBottom: '24px' }}>
              <h2 style={{ margin: '0 0 8px 0', color: '#1A3A2A' }}>Farm Decision Orchestrator</h2>
              <p style={{ margin: 0, color: '#5A6B5C', fontSize: '14px' }}>
                Coordinates validated microclimate epidemiological rules, APMC net freight realization, and safety-critical input differential diagnosis.
              </p>
            </div>

            {/* Input Form Panel */}
            <div style={{ backgroundColor: '#FFFFFF', padding: '24px', borderRadius: '8px', border: '1px solid #E0E6ED', marginBottom: '32px', display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '20px' }}>
              <div>
                <label style={{ display: 'block', fontSize: '12px', fontWeight: '600', marginBottom: '6px', color: '#37474F' }}>
                  CROP SELECTION (Tomato Pilot)
                </label>
                <select value={crop} onChange={(e) => setCrop(e.target.value)} style={{ width: '100%', padding: '10px', borderRadius: '6px', border: '1px solid #CFD8DC' }}>
                  <option value="Tomato">Tomato (Supported Pilot Crop)</option>
                  <option value="Chilli">Chilli (Unsupported - Validation Check)</option>
                  <option value="Cotton">Cotton (Unsupported - Validation Check)</option>
                </select>
              </div>

              <div>
                <label style={{ display: 'block', fontSize: '12px', fontWeight: '600', marginBottom: '6px', color: '#37474F' }}>DISTRICT</label>
                <select value={district} onChange={(e) => setDistrict(e.target.value)} style={{ width: '100%', padding: '10px', borderRadius: '6px', border: '1px solid #CFD8DC' }}>
                  <option value="Rangareddy">Rangareddy (Telangana)</option>
                  <option value="Siddipet">Siddipet (Telangana)</option>
                  <option value="Vikarabad">Vikarabad (Telangana)</option>
                </select>
              </div>

              <div>
                <label style={{ display: 'block', fontSize: '12px', fontWeight: '600', marginBottom: '6px', color: '#37474F' }}>
                  HARVEST QUANTITY (Quintals &gt; 0)
                </label>
                <input
                  type="number"
                  min="1"
                  value={quantity}
                  onChange={(e) => setQuantity(Number(e.target.value))}
                  style={{ width: '100%', padding: '10px', borderRadius: '6px', border: '1px solid #CFD8DC', boxSizing: 'border-box' }}
                />
              </div>

              <div style={{ gridColumn: 'span 2' }}>
                <label style={{ display: 'block', fontSize: '12px', fontWeight: '600', marginBottom: '6px', color: '#37474F' }}>OBSERVED CROP SYMPTOM / QUERY</label>
                <input
                  type="text"
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  style={{ width: '100%', padding: '10px', borderRadius: '6px', border: '1px solid #CFD8DC', boxSizing: 'border-box' }}
                />
              </div>

              <div style={{ display: 'flex', alignItems: 'flex-end' }}>
                <button
                  onClick={runDecisionCenter}
                  disabled={loading}
                  style={{
                    backgroundColor: '#1A3A2A',
                    color: '#FFFFFF',
                    padding: '12px 24px',
                    borderRadius: '6px',
                    border: 'none',
                    fontWeight: '600',
                    cursor: 'pointer',
                    width: '100%'
                  }}
                >
                  {loading ? 'Executing Multi-Agent Workflow...' : 'Execute Farm Decision Plan'}
                </button>
              </div>
            </div>

            {/* Results Grid */}
            {decisionResult && (
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(360px, 1fr))', gap: '24px' }}>
                {/* 1. Crop Guard Card */}
                <div style={{ backgroundColor: '#FFFFFF', padding: '24px', borderRadius: '8px', border: '1px solid #E0E6ED' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
                    <h3 style={{ margin: 0, color: '#1A3A2A' }}>🛡️ Crop Guard Assessment</h3>
                    <span style={{ fontSize: '11px', backgroundColor: '#FFF3E0', color: '#E65100', padding: '4px 8px', borderRadius: '4px', fontWeight: '600' }}>
                      RULE-BASED EPIDEMIOLOGY
                    </span>
                  </div>

                  <div style={{ fontSize: '12px', color: '#78909C', marginBottom: '12px' }}>
                    Weather Status: <strong>{decisionResult.weather_summary.status_label || 'LIVE MEASURED'}</strong>
                  </div>

                  {decisionResult.crop_guard.length === 0 ? (
                    <div style={{ fontSize: '13px', color: '#C62828' }}>
                      No assessments available. Crop '{crop}' is not supported by the Tomato pilot engine.
                    </div>
                  ) : (
                    decisionResult.crop_guard.map((cg: any, i: number) => (
                      <div key={i} style={{ borderBottom: '1px solid #ECEFF1', paddingBottom: '12px', marginBottom: '12px' }}>
                        <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                          <span style={{ fontWeight: '600', color: '#263238' }}>{cg.threat}</span>
                          <span style={{
                            fontSize: '11px',
                            fontWeight: '700',
                            padding: '2px 6px',
                            borderRadius: '3px',
                            backgroundColor: cg.risk_category === 'high' ? '#FFEBEE' : '#F1F8E9',
                            color: cg.risk_category === 'high' ? '#C62828' : '#2E7D32'
                          }}>
                            {cg.risk_category.toUpperCase()}
                          </span>
                        </div>
                        <div style={{ fontSize: '12px', color: '#546E7A', marginTop: '4px' }}>
                          Protocol: <code>{cg.model_or_rule_identifier}</code> • Category: {cg.threat_type}
                        </div>
                        <div style={{ fontSize: '12px', color: '#37474F', marginTop: '6px' }}>
                          👉 {cg.recommended_monitoring_action}
                        </div>
                      </div>
                    ))
                  )}
                </div>

                {/* 2. Input Trust Card */}
                <div style={{ backgroundColor: '#FFFFFF', padding: '24px', borderRadius: '8px', border: '1px solid #E0E6ED' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
                    <h3 style={{ margin: 0, color: '#1A3A2A' }}>🔬 Input Trust Diagnostic</h3>
                    <span style={{ fontSize: '11px', backgroundColor: '#FFEBEE', color: '#C62828', padding: '4px 8px', borderRadius: '4px', fontWeight: '600' }}>
                      DOSAGES DISABLED
                    </span>
                  </div>

                  <div style={{ fontSize: '13px', marginBottom: '12px', color: '#37474F' }}>
                    <strong>Differential Hypotheses:</strong>
                    <ul style={{ margin: '6px 0 0 0', paddingLeft: '18px', fontSize: '12px', color: '#546E7A' }}>
                      {decisionResult.input_trust.differential_diagnosis?.map((d: any, idx: number) => (
                        <li key={idx} style={{ marginBottom: '4px' }}>
                          <strong>{d.condition_name}</strong> ({d.probability_rank}): {d.differentiating_feature}
                        </li>
                      ))}
                    </ul>
                  </div>

                  <div style={{ backgroundColor: '#FBE9E7', padding: '12px', borderRadius: '6px', border: '1px solid #FFCCBC', fontSize: '12px', color: '#BF360C', marginBottom: '12px' }}>
                    ⚠️ <strong>Safety Directive:</strong> All synthetic chemical prescriptions and unverified dosages are disabled. Never apply chemicals without certified extension officer inspection.
                  </div>

                  <div style={{ fontSize: '12px', color: '#2E7D32' }}>
                    <strong>Recommended Cultural Controls:</strong>
                    <ul style={{ margin: '4px 0 0 0', paddingLeft: '18px', fontSize: '12px' }}>
                      {decisionResult.input_trust.non_chemical_cultural_controls?.map((c: string, idx: number) => (
                        <li key={idx} style={{ marginBottom: '4px' }}>{c}</li>
                      ))}
                    </ul>
                  </div>
                </div>

                {/* 3. Market Sense Card */}
                <div style={{ backgroundColor: '#FFFFFF', padding: '24px', borderRadius: '8px', border: '1px solid #E0E6ED' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
                    <h3 style={{ margin: 0, color: '#1A3A2A' }}>📈 Net Realization Optimizer</h3>
                    <span style={{ fontSize: '11px', backgroundColor: '#FFF3E0', color: '#E65100', padding: '4px 8px', borderRadius: '4px', fontWeight: '600' }}>
                      {decisionResult.market_sense?.recommended_mandi?.data_source || 'DEMO_SIMULATED'}
                    </span>
                  </div>

                  {decisionResult.market_sense?.recommended_mandi && (
                    <div>
                      <div style={{ backgroundColor: '#F1F8E9', padding: '14px', borderRadius: '6px', marginBottom: '14px' }}>
                        <div style={{ fontSize: '16px', fontWeight: '700', color: '#1A3A2A' }}>
                          {decisionResult.market_sense.recommended_mandi.market_name} (Rank #1)
                        </div>
                        <div style={{ fontSize: '13px', color: '#33691E', marginTop: '4px' }}>
                          Net Realization: <strong>₹{decisionResult.market_sense.recommended_mandi.net_realization_per_quintal.toFixed(2)}/qtl</strong>
                        </div>
                        <div style={{ fontSize: '13px', color: '#558B2F' }}>
                          Total Net Payout: <strong>₹{decisionResult.market_sense.recommended_mandi.expected_net_realization.toLocaleString()}</strong> (for {quantity} qtl)
                        </div>
                      </div>

                      <div style={{ fontSize: '12px', color: '#546E7A', marginBottom: '10px' }}>
                        <strong>Transparent Cost Disclosures:</strong>
                        <div style={{ marginTop: '4px' }}>
                          • Freight: ₹{decisionResult.market_sense.recommended_mandi.transport_cost} ({decisionResult.market_sense.recommended_mandi.cost_assumptions?.trucks_allocated} truck(s))<br/>
                          • Mandi Fee: ₹{decisionResult.market_sense.recommended_mandi.mandi_fees} (1%)<br/>
                          • Handling Hamali: ₹{decisionResult.market_sense.recommended_mandi.handling_cost} (₹35/qtl)<br/>
                          • Quality Transit Deduction: ₹{decisionResult.market_sense.recommended_mandi.transit_quality_loss}
                        </div>
                      </div>
                    </div>
                  )}
                </div>

                {/* 4. Supervisor Advisory */}
                <div style={{ backgroundColor: '#1A3A2A', color: '#FFFFFF', padding: '24px', borderRadius: '8px', gridColumn: 'span 2' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px' }}>
                    <h3 style={{ margin: 0, color: '#D4AF37' }}>🤖 Farmer Advisory Synthesis</h3>
                    <span style={{ fontSize: '11px', backgroundColor: 'rgba(255,255,255,0.15)', padding: '4px 8px', borderRadius: '4px' }}>
                      Google AI / Gemini Synthesis
                    </span>
                  </div>
                  <p style={{ lineHeight: '1.6', fontSize: '14px', margin: '0 0 16px 0', opacity: 0.95 }}>
                    {decisionResult.synthesized_explanation?.explanation_text}
                  </p>
                  <div style={{ backgroundColor: 'rgba(0,0,0,0.25)', padding: '12px', borderRadius: '6px', fontSize: '12px' }}>
                    🔒 <strong>Compliance Notice:</strong> {decisionResult.synthesized_explanation?.safety_reminder}
                  </div>
                </div>
              </div>
            )}
          </div>
        )}

        {activeTab === 'governance' && (
          <div style={{ backgroundColor: '#FFFFFF', padding: '24px', borderRadius: '8px', border: '1px solid #E0E6ED' }}>
            <h2 style={{ color: '#1A3A2A', margin: '0 0 16px 0' }}>Data Governance & Honest ML Status</h2>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '20px' }}>
              <div style={{ border: '1px solid #CFD8DC', padding: '16px', borderRadius: '6px' }}>
                <h4 style={{ margin: '0 0 8px 0', color: '#263238' }}>APMC Price Model</h4>
                <p style={{ fontSize: '12px', color: '#546E7A' }}>Algorithm: Random Forest Regressor</p>
                <p style={{ fontSize: '12px', color: '#546E7A' }}>Operational Status: <strong>SIMULATION_ONLY</strong></p>
                <span style={{ fontSize: '11px', backgroundColor: '#FFF3E0', color: '#E65100', padding: '2px 6px', borderRadius: '4px' }}>
                  NOT REAL-WORLD CERTIFIED
                </span>
              </div>
              <div style={{ border: '1px solid #CFD8DC', padding: '16px', borderRadius: '6px' }}>
                <h4 style={{ margin: '0 0 8px 0', color: '#263238' }}>Open-Meteo High Resolution</h4>
                <p style={{ fontSize: '12px', color: '#546E7A' }}>Provenance: <code>PROV-WEATHER-003</code></p>
                <p style={{ fontSize: '12px', color: '#546E7A' }}>Status: Live API connected when online</p>
                <span style={{ fontSize: '11px', backgroundColor: '#E8F5E9', color: '#2E7D32', padding: '2px 6px', borderRadius: '4px' }}>VERIFIED TELEMETRY</span>
              </div>
              <div style={{ border: '1px solid #CFD8DC', padding: '16px', borderRadius: '6px' }}>
                <h4 style={{ margin: '0 0 8px 0', color: '#263238' }}>Crop Disease DL Vision</h4>
                <p style={{ fontSize: '12px', color: '#546E7A' }}>Architecture: EfficientNet / MobileNet</p>
                <p style={{ fontSize: '12px', color: '#546E7A' }}>Operational Status: <strong>NOT_TRAINED</strong></p>
                <span style={{ fontSize: '11px', backgroundColor: '#ECEFF1', color: '#607D8B', padding: '2px 6px', borderRadius: '4px' }}>NO FAKE WEIGHTS</span>
              </div>
            </div>
          </div>
        )}
      </main>

      {/* Footer */}
      <footer style={{ backgroundColor: '#FFFFFF', borderTop: '1px solid #E0E6ED', padding: '16px 32px', textAlign: 'center', fontSize: '12px', color: '#78909C' }}>
        KRISHIVA AI • Buildathon Edition • Evidence-led agricultural intelligence with strict regulatory and safety boundaries.
      </footer>
    </div>
  );
};

export default App;
