import { useState } from 'react'
import { Link } from 'react-router-dom'
import { demanderReinitialisationMdp } from '../../services/authService'
import './Login.css'
import './ForgotPassword.css'

export default function ForgotPassword() {
  const [email, setEmail] = useState('')
  const [envoye, setEnvoye] = useState(false)
  const [erreur, setErreur] = useState('')
  const [chargement, setChargement] = useState(false)

  const handleSubmit = async (e) => {
    e.preventDefault()
    setErreur('')
    if (!email.trim()) {
      setErreur('Veuillez saisir votre adresse email.')
      return
    }
    setChargement(true)
    try {
      await demanderReinitialisationMdp(email)
      setEnvoye(true)
    } catch (err) {
      setErreur(err.response?.data?.message || 'Une erreur est survenue. Réessayez.')
    } finally {
      setChargement(false)
    }
  }

  return (
    <div className="login-page forgot-page">
      <div className="login-right" style={{ width: '100%', maxWidth: 480, margin: '0 auto' }}>
        <div className="login-card">
          <div className="forgot-back">
            <Link to="/login">← Retour à la connexion</Link>
          </div>

          <h2 className="login-title">Mot de passe oublié</h2>

          {!envoye ? (
            <>
              <p className="login-hint" style={{ marginBottom: 24 }}>
                Saisissez votre adresse email. Vous recevrez un lien pour réinitialiser votre mot de passe.
              </p>
              {erreur && <div className="alert alert-danger">{erreur}</div>}
              <form onSubmit={handleSubmit}>
                <div className="form-group">
                  <label className="form-label">Adresse email</label>
                  <input
                    type="email"
                    className="form-control"
                    placeholder="votre.email@exemple.com"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    autoFocus
                  />
                </div>
                <button
                  type="submit"
                  className="btn btn-primary btn-lg login-submit"
                  disabled={chargement}
                >
                  {chargement ? (
                    <><div className="spinner" style={{ width: 18, height: 18 }}></div> Envoi en cours...</>
                  ) : (
                    'Envoyer le lien'
                  )}
                </button>
              </form>
            </>
          ) : (
            <div className="forgot-success">
              <h3>Email envoyé !</h3>
              <p>
                Un lien de réinitialisation a été envoyé à <strong>{email}</strong>.
                Vérifiez votre boîte de réception (et vos spams).
              </p>
              <p className="forgot-expire">Le lien expire dans 30 minutes.</p>
              <Link to="/login" className="btn btn-secondary" style={{ marginTop: 20 }}>
                Retour à la connexion
              </Link>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
