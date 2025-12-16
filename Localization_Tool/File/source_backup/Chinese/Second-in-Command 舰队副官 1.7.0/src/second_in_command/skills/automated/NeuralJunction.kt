package second_in_command.skills.automated

import com.fs.starfarer.api.Global
import com.fs.starfarer.api.combat.MutableShipStatsAPI
import com.fs.starfarer.api.combat.ShipAPI
import com.fs.starfarer.api.combat.ShipVariantAPI
import com.fs.starfarer.api.impl.campaign.ids.Strings
import com.fs.starfarer.api.ui.TooltipMakerAPI
import com.fs.starfarer.api.util.Misc
import org.magiclib.kotlin.isAutomated
import second_in_command.SCData
import second_in_command.specs.SCBaseSkillPlugin

class NeuralJunction : SCBaseSkillPlugin() {

    override fun getAffectsString(): String {
        return "座舰"
    }

    override fun addTooltip(data: SCData, tooltip: TooltipMakerAPI) {

        tooltip.addPara("使玩家可以直接操控自动化舰船", 0f, Misc.getHighlightColor(), Misc.getHighlightColor())
        tooltip.addPara("   - 玩家的无人舰点数倍率为 1${Strings.X}", 0f, Misc.getTextColor(), Misc.getHighlightColor(), "1${Strings.X}")
        tooltip.addPara("   - 玩家操控的自动化舰船 +15%% 战备值 (CR) 上限", 0f, Misc.getTextColor(), Misc.getHighlightColor(), "+15%")
        tooltip.addPara("   - 如果该执行军官被撤销指派，玩家将被转移至其他舰船", 0f, Misc.getTextColor(), Misc.getHighlightColor())

    }

    override fun applyEffectsBeforeShipCreation(data: SCData?, stats: MutableShipStatsAPI?, variant: ShipVariantAPI?, hullSize: ShipAPI.HullSize?, id: String?) {

        var captain = stats!!.fleetMember?.captain
        if (stats.isAutomated() && captain != null && captain == Global.getSector().playerPerson) {
            stats!!.maxCombatReadiness.modifyFlat("sc_crew_training", 0.15f, "神经接口")
        }


    }

    override fun onDeactivation(data: SCData) {
        var playership = Global.getSector().playerFleet.fleetData.membersListCopy.find { it.captain?.isPlayer == true } ?: return

        if (Misc.isAutomated(playership)) {
            var members = Global.getSector().playerFleet.fleetData.membersListCopy
            var nonAutomatedShip = members.find { !Misc.isAutomated(it) && (it.captain == null || it.captain.isDefault) }
            if (nonAutomatedShip == null) {
                nonAutomatedShip = members.find { !Misc.isAutomated(it)}
            }

            if (nonAutomatedShip != null) {
                nonAutomatedShip.captain = Global.getSector().playerPerson
                playership.captain = null
            }
        }
    }

}