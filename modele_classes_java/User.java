package com.moov.facturation.utilisateurs;

import java.util.Date;
import java.util.List;

/**
 * Représente un utilisateur du système
 * Rôles : Admin, Chef, Agent, Payeur, Employé
 */
public class User {
    
    // Attributs
    private String id;
    private String email;
    private String firstName;
    private String lastName;
    private RoleChoices role;
    private StatusChoices status;
    private String telephone;
    
    // Relations
    private List<StatusHistory> statusHistory;
    private User createdBy;
    private List<User> createdUsers;
    private User statusChangedBy;
    private List<User> changedStatuses;
    private List<Company> companies;
    private List<Line> lines;
    private List<AuditContrat> auditContrats;
    private List<HistoriqueFacturation> historiqueFacturations;
    private List<Publication> publications;
    
    // Méthodes
    public boolean hasPermission(String permission) {
        return false;
    }
    
    // Getters et Setters
    public String getId() { return id; }
    public void setId(String id) { this.id = id; }
    
    public String getEmail() { return email; }
    public void setEmail(String email) { this.email = email; }
    
    public String getFirstName() { return firstName; }
    public void setFirstName(String firstName) { this.firstName = firstName; }
    
    public String getLastName() { return lastName; }
    public void setLastName(String lastName) { this.lastName = lastName; }
    
    public RoleChoices getRole() { return role; }
    public void setRole(RoleChoices role) { this.role = role; }
    
    public StatusChoices getStatus() { return status; }
    public void setStatus(StatusChoices status) { this.status = status; }
    
    public String getTelephone() { return telephone; }
    public void setTelephone(String telephone) { this.telephone = telephone; }
}
