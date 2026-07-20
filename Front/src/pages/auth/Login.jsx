import { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { useAuth } from '../../contexts/AuthContext'
import { login as loginService } from '../../services/authService'
import { enregistrerVisite } from '../../services/deviceService'
import illustrationFactures from '../../assets/illustration-factures.svg'
import logoMoov from '../../assets/logo-moov.png'
import './Login.css'

export default function Login() {
  const navigate = useNavigate()
  const { login } = useAuth()

  const [identifiant, setIdentifiant] = useState('')
  const [motDePasse, setMotDePasse] = useState('')
  const [showPassword, setShowPassword] = useState(false)
  const [erreur, setErreur] = useState('')
  const [chargement, setChargement] = useState(false)

  const handleSubmit = async (e) => {
    e.preventDefault()
    setErreur('')
    if (!identifiant.trim() || !motDePasse.trim()) {
      setErreur('Veuillez remplir tous les champs.')
      return
    }
    setChargement(true)
    try {
      // Le type est déduit automatiquement par le backend selon l'identifiant
      const data = await loginService(identifiant, motDePasse, null)
      login(data.token, data.user)
      enregistrerVisite(data.user.id, data.user.role)
      // Redirection selon le rôle
      if (data.user.role === 'SUPER_ADMIN') {
        navigate('/admin/dashboard')
      } else if (data.user.role === 'AGENT_FACTURATION') {
        navigate('/agent/dashboard')
      } else {
        navigate('/dashboard')
      }
    } catch (err) {
      setErreur(err.response?.data?.message || 'Identifiant ou mot de passe incorrect.')
    } finally {
      setChargement(false)
    }
  }

  return (
    <div className="login-page">

      {/* ── Panneau gauche : branding ── */}
      <div className="login-left">

        {/* Logo Moov Africa — coin supérieur droit du panneau bleu */}
        <div className="login-branding-logo">
          <img src={logoMoov} alt="Moov Africa" className="login-branding-logo-img" />
        </div>

        {/* Losanges style Moov Africa */}
        <div className="login-triangles">

          {/* ── COIN HAUT-GAUCHE ── */}
          <div style={{
            position: 'absolute',
            top: '-30px',
            left: '-30px',
            width: '220px',
            height: '220px',
            borderRadius: '38px',
            background: 'linear-gradient(135deg, #78b4dc, #2d6ea8)',
            transform: 'rotate(45deg)',
            transformOrigin: 'center',
            zIndex: 0,
          }} />
          <div style={{
            position: 'absolute',
            top: '-10px',
            left: '-10px',
            width: '200px',
            height: '200px',
            borderRadius: '34px',
            background: 'linear-gradient(135deg, #fac278, #f08020)',
            transform: 'rotate(45deg)',
            transformOrigin: 'center',
            zIndex: 1,
          }} />

          {/* ── COIN BAS-DROIT ── */}
          <div style={{
            position: 'absolute',
            bottom: '-30px',
            right: '-30px',
            width: '280px',
            height: '280px',
            borderRadius: '45px',
            background: 'linear-gradient(135deg, #fac278, #f08020)',
            transform: 'rotate(45deg)',
            transformOrigin: 'center',
            zIndex: 0,
          }} />
          <div style={{
            position: 'absolute',
            bottom: '-10px',
            right: '-10px',
            width: '260px',
            height: '260px',
            borderRadius: '42px',
            background: 'linear-gradient(135deg, #78b4dc, #2d6ea8)',
            transform: 'rotate(45deg)',
            transformOrigin: 'center',
            zIndex: 1,
          }} />

        </div>

        <div className="login-left-inner">

          {/* Logo */}
          <div className="login-logo">
            <span className="logo-moov">moov</span>
            <span className="logo-africa">Africa</span>
            <span className="logo-ebillings">e-Billings</span>
          </div>

          {/* Titre portail */}
          <h1 className="login-tagline">
            Portail de publication<br />de factures clients
          </h1>
          <p className="login-subtitle">
            Accédez à vos factures postpayées, suivez votre consommation et simulez vos prochaines dépenses.
          </p>

          {/* Illustration factures */}
          <div className="login-illustration">
            <img
              src={illustrationFactures}
              alt="Illustration publication de factures"
              className="login-illustration-img"
            />
          </div>

        </div>
      </div>

      {/* ── Panneau droit : formulaire ── */}
      <div className="login-right">
        <div className="login-card">

          {/* En-tête carte */}
          <div className="login-card-header">
            <div className="login-card-logo">
              {/* Icône signal / réseau — évoque un opérateur télécom */}
              <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/>
              </svg>
            </div>
            <div>
              <h2 className="login-title">Connexion</h2>
              <p className="login-hint">Portail e-Billings — Moov Africa Togo</p>
            </div>
          </div>

          {/* Message d'erreur */}
          {erreur && (
            <div className="alert alert-danger login-alert">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>
              {erreur}
            </div>
          )}

          {/* Formulaire */}
          <form onSubmit={handleSubmit} noValidate>
            <div className="form-group">
              <label className="form-label">Identifiant</label>
              <div className="input-icon-wrap">
                <span className="input-icon">
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>
                </span>
                <input
                  type="text"
                  className="form-control form-control-icon"
                  placeholder="Email, n° de contrat ou n° de ligne"
                  value={identifiant}
                  onChange={(e) => setIdentifiant(e.target.value)}
                  autoFocus
                  autoComplete="username"
                />
              </div>
            </div>

            <div className="form-group">
              <label className="form-label">Mot de passe</label>
              <div className="input-icon-wrap">
                <span className="input-icon">
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><rect x="3" y="11" width="18" height="11" rx="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/></svg>
                </span>
                <input
                  type={showPassword ? 'text' : 'password'}
                  className="form-control form-control-icon form-control-icon-right"
                  placeholder="Votre mot de passe"
                  value={motDePasse}
                  onChange={(e) => setMotDePasse(e.target.value)}
                  autoComplete="current-password"
                />
                <button
                  type="button"
                  className="input-eye-btn"
                  onClick={() => setShowPassword(p => !p)}
                  tabIndex={-1}
                  aria-label={showPassword ? 'Masquer le mot de passe' : 'Afficher le mot de passe'}
                >
                  {showPassword ? (
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94"/><path d="M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19"/><line x1="1" y1="1" x2="23" y2="23"/></svg>
                  ) : (
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/></svg>
                  )}
                </button>
              </div>
            </div>

            <div className="login-forgot">
              <Link to="/forgot-password">Mot de passe oublié ?</Link>
            </div>

            <button
              type="submit"
              className="btn btn-primary login-submit"
              disabled={chargement}
            >
              {chargement ? (
                <><div className="spinner" style={{ width: 18, height: 18, borderTopColor: 'white' }}></div> Connexion...</>
              ) : (
                <>
                  Se connecter
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5"><path d="M5 12h14"/><path d="m12 5 7 7-7 7"/></svg>
                </>
              )}
            </button>
          </form>

          <p className="login-footer-note">
            En cas de problème de connexion, contactez votre administrateur Moov Africa Togo.
          </p>
        </div>
      </div>
    </div>
  )
}
