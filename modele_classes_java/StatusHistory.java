package com.moov.facturation.utilisateurs;

import java.util.Date;

/**
 * Historique des changements de statut utilisateur
 */
public class StatusHistory {
    
    // Attributs
    private String id;
    private String oldStatus;
    private String newStatus;
    private Date changedAt;
    
    // Relations
    private User user;
    private User changedBy;
    
    // Getters et Setters
    public String getId() { return id; }
    public void setId(String id) { this.id = id; }
    
    public String getOldStatus() { return oldStatus; }
    public void setOldStatus(String oldStatus) { this.oldStatus = oldStatus; }
    
    public String getNewStatus() { return newStatus; }
    public void setNewStatus(String newStatus) { this.newStatus = newStatus; }
    
    public Date getChangedAt() { return changedAt; }
    public void setChangedAt(Date changedAt) { this.changedAt = changedAt; }
    
    public User getUser() { return user; }
    public void setUser(User user) { this.user = user; }
    
    public User getChangedBy() { return changedBy; }
    public void setChangedBy(User changedBy) { this.changedBy = changedBy; }
}
