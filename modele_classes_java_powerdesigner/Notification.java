package com.moovafrica.powerdesigner;

import jakarta.persistence.*;
import java.time.LocalDateTime;
import java.util.UUID;

@Entity
@Table(name = "notifications")
public class Notification {
    @Id
    private UUID id;

    @ManyToOne(optional = false)
    @JoinColumn(name = "utilisateur_id", nullable = false)
    private Utilisateur utilisateur; // Utilisateur 1 -> 0..* Notification

    @Enumerated(EnumType.STRING)
    private CanalNotificationCode canal;

    private String titre;

    @Column(columnDefinition = "TEXT")
    private String message;

    @Enumerated(EnumType.STRING)
    private StatutNotificationCode statut;

    private boolean estLue;
    private LocalDateTime createdAt;
}
