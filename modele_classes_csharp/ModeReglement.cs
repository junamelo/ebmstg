namespace Moov.Facturation.Contrats
{
    /// <summary>
    /// Enumération des modes de règlement
    /// </summary>
    public enum ModeReglement
    {
        /// <summary>
        /// Paiement par chèque
        /// </summary>
        CHEQUE,
        
        /// <summary>
        /// Paiement par virement bancaire
        /// </summary>
        VIREMENT,
        
        /// <summary>
        /// Paiement en espèces
        /// </summary>
        ESPECES
    }
}
