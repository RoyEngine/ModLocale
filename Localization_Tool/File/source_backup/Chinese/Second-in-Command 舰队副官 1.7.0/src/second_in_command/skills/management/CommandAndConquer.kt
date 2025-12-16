package second_in_command.skills.management

import com.fs.starfarer.api.Global
import com.fs.starfarer.api.combat.MutableShipStatsAPI
import com.fs.starfarer.api.combat.ShipAPI
import com.fs.starfarer.api.combat.ShipVariantAPI
import com.fs.starfarer.api.impl.campaign.ids.Stats
import com.fs.starfarer.api.ui.TooltipMakerAPI
import com.fs.starfarer.api.util.Misc
import second_in_command.SCData
import second_in_command.specs.SCBaseSkillPlugin

class CommandAndConquer : SCBaseSkillPlugin() {

    override fun getAffectsString(): String {
        return "舰队"
    }

    override fun addTooltip(data: SCData, tooltip: TooltipMakerAPI) {

        tooltip.addPara("+3 指挥点", 0f, Misc.getHighlightColor(), Misc.getHighlightColor())
        tooltip.addPara("+50%% 指挥点回复速度", 0f, Misc.getHighlightColor(), Misc.getHighlightColor())

        if (data.isPlayer) {
            tooltip.addPara("即使未占领任何目标点，仍能给予当前战斗规模 5%% 的部署点奖励", 0f, Misc.getHighlightColor(), Misc.getHighlightColor())
        }

    }

    override fun applyEffectsBeforeShipCreation(data: SCData, stats: MutableShipStatsAPI?, variant: ShipVariantAPI, hullSize: ShipAPI.HullSize?, id: String?) {

    }

    override fun applyEffectsAfterShipCreation(data: SCData, ship: ShipAPI?, variant: ShipVariantAPI, id: String?) {
        data.commander.stats.commandPoints.modifyFlat("sc_command_and_conquer", 3f)
        data.commander.stats.dynamic.getMod(Stats.COMMAND_POINT_RATE_FLAT).modifyFlat("sc_command_and_conquer", 0.5f)

        if (data.isPlayer) {
            data.commander.stats.getDynamic().getMod(Stats.DEPLOYMENT_POINTS_MIN_FRACTION_OF_BATTLE_SIZE_BONUS_MOD)
                .modifyFlat("sc_command_and_conquer", 0.05f)
        }

    }

    override fun advance(data: SCData, amount: Float) {

        data.commander.stats.commandPoints.modifyFlat("sc_command_and_conquer", 3f)
        data.commander.stats.dynamic.getMod(Stats.COMMAND_POINT_RATE_FLAT).modifyFlat("sc_command_and_conquer", 0.5f)

        if (data.isPlayer) {
            data.commander.stats.getDynamic().getMod(Stats.DEPLOYMENT_POINTS_MIN_FRACTION_OF_BATTLE_SIZE_BONUS_MOD)
                .modifyFlat("sc_command_and_conquer", 0.05f)
        }

    }

    override fun onDeactivation(data: SCData) {

        data.commander.stats.commandPoints.unmodify("sc_command_and_conquer")
        data.commander.stats.dynamic.getMod(Stats.COMMAND_POINT_RATE_FLAT).unmodify("sc_command_and_conquer")

        if (data.isPlayer) {
            data.commander.stats.getDynamic().getMod(Stats.DEPLOYMENT_POINTS_MIN_FRACTION_OF_BATTLE_SIZE_BONUS_MOD)
                .unmodify("sc_command_and_conquer")
        }
    }

}