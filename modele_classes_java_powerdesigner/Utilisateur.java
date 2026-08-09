package com.moovafrica.powerdesigner;

import jakarta.persistence.*;
import java.time.LocalDateTime;
import java.util.ArrayList;
import java.util.List;
import java.util.UUID;

@Entity
@Table(name = "utilisateurs")
@Inheritance(strategy = InheritanceType.JOINED)
public abstract class Utilisateur {
    @Id
    protected UUID id;

    @Column(nullable = false)
    protected String email;

    @Column(nullable = false)
    protected String nomComplet;

    @Column(nullable = false)
    protected String motDePasseHash;

    protected String telephone;
    protected boolean estActif;
    protected LocalDateTime derniereConnexion;
    protected LocalDateTime createdAt;
    protected LocalDateTime updatedAt;

    @ManyToOne(optional = false)
    @JoinColumn(name = "role_id", nullable = false)
    protected Role role; // Utilisateur 1 -> 1 Role

    @OneToMany(mappedBy = "utilisateur")
    protected List<Notification> notifications = new ArrayList<>(); // Utilisateur 1 -> 0..* Notification

    @OneToMany(mappedBy = "utilisateur")
    protected List<SessionUtilisateur> sessions = new ArrayList<>(); // Utilisateur 1 -> 0..* Session

    @OneToMany(mappedBy = "utilisateur")
    protected List<PasswordReset> demandesReset = new ArrayList<>(); // Utilisateur 1 -> 0..* PasswordReset

    @OneToMany(mappedBy = "utilisateur")
    protected List<Simulation> simulations = new ArrayList<>(); // Utilisateur 1 -> 0..* Simulation
}
