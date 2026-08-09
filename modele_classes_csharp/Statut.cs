namespace Moov.Facturation.Facturation
{
    /// <summary>
    /// Enumération des statuts de notification
    /// </summary>
    public enum Statut
    {
        /// <summary>
        /// Notification envoyée avec succès
        /// </summary>
        ENVOYEE,
        
        /// <summary>
        /// Echec d'envoi de la notification
        /// </summary>
        ECHEC,
        
        /// <summary>
        /// Canal non configuré
        /// </summary>
        NON_CONFIGUREE
    }
}
