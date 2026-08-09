package com.moovafrica.powerdesigner;

import jakarta.persistence.*;
import java.time.LocalDateTime;
import java.util.UUID;

@Entity
@Table(name = "password_resets")
public class PasswordReset {
    @Id
    private UUID id;

    @ManyToOne(optional = false)
    @JoinColumn(name = "utilisateur_id", nullable = false)
    private Utilisateur utilisateur; // Utilisateur 1 -> 0..* PasswordReset

    @Column(nullable = false)
    private String token;

    private LocalDateTime expireAt;
    private boolean estValide;
    private boolean estUtilise;
}
