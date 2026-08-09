namespace Moov.Facturation.Facturation
{
    /// <summary>
    /// Notification envoyée pour une facture
    /// </summary>
    public class NotificationFacture
    {
        // Attributs
        public string Id { get; set; }
        public Canal Canal { get; set; }
        public string Destinataire { get; set; }
        public Statut Statut { get; set; }
        
        // Relations
        public Invoice Invoice { get; set; }
    }
}
